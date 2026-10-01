import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Fleet, GpuStatus } from '../types'

const status = atom({ plugin: 'della-gpu', key: 'status' } as const, null)
const fleet = atom({ plugin: 'della-gpu', key: 'fleet' } as const, null)
const isHidden = atom({ plugin: 'della-gpu', key: 'isHidden' } as const, false)

const PANE = 'della-fleet'
const POLL_MS = 120_000

// Shared 90 s cache on /scratch so several sessions do not each hit slurmctld.
const STATUS_SH = String.raw`
C=/scratch/gpfs/KARTHIKN/wc9403/tmp/.della-gpu-status.json
now=$(date +%s)
if [ -f "$C" ] && [ $((now - $(stat -c %Y "$C"))) -lt 90 ]; then cat "$C"; exit 0; fi
command -v squeue >/dev/null || exit 3
T=$(mktemp)
N=$(sinfo -h -p pli-c -o %N | paste -sd,)
squeue -h -t R -w "$N" -O "UserName:20,tres-alloc:240" | awk '{g=0; if (match($2,/gres\/gpu=[0-9]+/)) g=substr($2,RSTART+9,RLENGTH-9)+0; G[$1]+=g} END{for (u in G) if (G[u]>0) print G[u], u}' | sort -k1,1nr > "$T"
mine=$(awk -v me="$USER" '$2==me{print $1}' "$T"); rank=$(awk -v me="$USER" '$2==me{print NR}' "$T")
users=$(wc -l < "$T")
top=$(head -5 "$T" | awk '{printf "%s[\"%s\",%d]", (NR>1?",":""), $2, $1}')
read pj pg < <(squeue -u "$USER" -t PD -h -r -o "%b|%D" | awk -F'|' '/gpu/{n++; k=split($1,a,":"); g+=a[k]*$2} END{print n+0, g+0}')
read used total free < <(sinfo -h -p pli-c -N -O "StateComplete:40,Gres:40,GresUsed:60" | awk '{t=0;u=0; if (match($2,/gpu:h100:[0-9]+/)) t=substr($2,RSTART+9,RLENGTH-9)+0; if (match($3,/gpu:h100:[0-9]+/)) u=substr($3,RSTART+9,RLENGTH-9)+0; T+=t; U+=u; if ($1 !~ /drain|down|planned|maint|reserved/) F+=t-u} END{print U+0, T+0, F+0}')
rm -f "$T"
[ -z "$mine" ] && mine=0
[ -z "$rank" ] && rank=0
printf '{"at":%d,"mine":%d,"pendJobs":%d,"pendGpus":%d,"rank":%d,"users":%d,"used":%d,"total":%d,"free":%d,"top":[%s]}\n' \
  "$now" "$mine" "$pj" "$pg" "$rank" "$users" "$used" "$total" "$free" "$top" > "$C.$$" && mv -f "$C.$$" "$C"
cat "$C"
`

const FLEET_SH = String.raw`
echo "@S"
for s in $(tmux ls -F '#{session_name}' 2>/dev/null); do
  last=$(tmux capture-pane -t "$s" -p -J 2>/dev/null | awk '{L[NR]=$0} /^❯/{p=NR} END{for (i=p-1;i>0;i--) {x=L[i]; if (x ~ /^[[:space:]]*$/ || x ~ /^[[:space:]]*[─━╭╰│]/ || x ~ /esc to interrupt|Update installed/) continue; print x; break}}' | sed 's/^[[:space:]]*//' | cut -c1-120)
  printf '%s\t%s\n' "$s" "$last"
done
echo "@J"
squeue -u "$USER" -h -o "%T|%Z|%b|%D" | awk -F'|' '{n=split($2,p,"/"); d=p[n]; g=0; if (match($3,/gpu(:h100)?:[0-9]+/)) {s=substr($3,RSTART,RLENGTH); k=split(s,a,":"); g=a[k]*$4} D[d]=1; if ($1=="RUNNING") R[d]+=g; else if ($1=="PENDING" && g>0) P[d]++} END{for (d in D) printf "%s\t%d\t%d\n", d, R[d], P[d]}' | sort -t$'\t' -k2,2nr
echo "@Q"
checkquota -f KARTHIKN -u 2>/dev/null | awk -v me="$USER" '/^TOTAL/{printf "group %s / %s, files %s / %s\n", $2, $3, $4, $5} $1==me{for (i=2;i<=NF;i++) if ($i ~ /iB$/) {printf "mine %s, files %s\n", $i, $NF; break}}'
`

function parseFleet(text: string, at: number): Fleet {
  const out: Fleet = { at, sessions: [], jobs: [], quota: '' }
  let section = ''
  for (const line of text.split('\n')) {
    if (line.startsWith('@')) {
      section = line
      continue
    }
    if (!line.trim()) continue
    const cols = line.split('\t')
    if (section === '@S') out.sessions.push({ name: cols[0] ?? '', last: cols[1] ?? '' })
    if (section === '@J') out.jobs.push({ dir: cols[0] ?? '', runGpus: Number(cols[1] ?? 0), pendJobs: Number(cols[2] ?? 0) })
    if (section === '@Q') out.quota = out.quota ? `${out.quota} · ${line}` : line
  }
  return out
}

let isFleetWanted = false

async function refreshStatus($: EngineInterface) {
  try {
    const r = await $.process.run(['bash', '-c', STATUS_SH], { timeoutMs: 60_000 })
    if (r.exitCode !== 0) return
    const s = JSON.parse(r.stdout.trim().split('\n').pop() ?? '') as GpuStatus
    await update($, status, () => s)
  } catch {
    // squeue hiccups are transient; the next tick retries.
  }
}

async function refreshFleet($: EngineInterface) {
  try {
    const r = await $.process.run(['bash', '-c', FLEET_SH], { timeoutMs: 60_000 })
    const at = await $.clock.now()
    await update($, fleet, () => parseFleet(r.stdout, at))
  } catch {
    // keep the last good view
  }
}


export const register: Register = on => {

  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'fleet', description: 'Open the Della fleet pane: tmux sessions, jobs per project, quota' })
    await $.command.register({ name: 'gpu', description: 'Della GPU status now, in a pane every surface shows (phone and desktop included)' })
    void refreshStatus($)
    $.clock.every(POLL_MS, () => {
      void refreshStatus($)
      if (isFleetWanted) void refreshFleet($)
    })
    return next(e)
  })

  on('command.run', { command: 'fleet' }, async $ => {
    isFleetWanted = true
    await Promise.all([refreshStatus($), refreshFleet($)])
    await $.ui.open({ id: PANE, title: 'Della fleet' })
    const s = await read($, status)
    const f = await read($, fleet)
    const lines: string[] = []
    if (s) lines.push(`GPU: ${s.mine} running, ${s.pendJobs} pending jobs (${s.pendGpus} GPUs), rank ${s.rank}/${s.users}, pli-c ${s.used}/${s.total}, free ${s.free}`)
    if (f) {
      lines.push('Sessions:')
      for (const one of f.sessions) lines.push(`  ${one.name}: ${one.last || '-'}`)
      lines.push('Jobs by workdir (running GPUs / pending GPU jobs):')
      for (const one of f.jobs) lines.push(`  ${one.dir}: ${one.runGpus} / ${one.pendJobs}`)
      if (f.quota) lines.push(`Quota: ${f.quota}`)
    }
    return { text: lines.length ? lines.join('\n') : 'Fleet unavailable.' }
  })

  on('command.run', { command: 'gpu' }, async $ => {
    await update($, isHidden, () => false)
    isFleetWanted = true
    await Promise.all([refreshStatus($), refreshFleet($)])
    await $.ui.open({ id: PANE, title: 'Della GPU' })
    const s = await read($, status)
    return { text: s ? `GPU: ${s.mine} running, ${s.pendJobs} pending jobs (${s.pendGpus} GPUs), rank ${s.rank}/${s.users}, pli-c ${s.used}/${s.total}, free ${s.free}` : 'GPU status unavailable (no squeue here?).' }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const s = await read($, status)
    if (e.props.hasSurvey || s === null || (await read($, isHidden))) return next(e)
    const { Box, Button, Text } = $.ui.resolve(e)
    const rank = s.rank > 0 ? `#${s.rank}/${s.users}` : 'unranked'
    return (
      <Box>
        <Text dimColor>
          GPU {s.mine} running · {s.pendJobs} pending ({s.pendGpus}) · {rank} · pli-c {s.used}/{s.total}, {s.free} free{' '}
        </Text>
        <Button key="hide" label="Hide" onPress={() => update($, isHidden, () => true)} />
      </Box>
    )
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const s = await read($, status)
    const f = await read($, fleet)
    return (
      <Box flexDirection="column">
        {s && (
          <Text>
            GPU {s.mine} running, {s.pendJobs} pending ({s.pendGpus}); rank {s.rank}/{s.users}; pli-c {s.used}/{s.total}, {s.free} free
          </Text>
        )}
        {s && <Text dimColor>top: {s.top.map(([u, g]) => `${u} ${g}`).join(', ')}</Text>}
        {f === null && <Text dimColor>Loading…</Text>}
        {f && <Text bold>Sessions</Text>}
        {f?.sessions.map(one => (
          <Text>
            {one.name.padEnd(15)} <Text dimColor>{one.last || '-'}</Text>
          </Text>
        ))}
        {f && <Text bold>Jobs by workdir (running GPUs / pending GPU jobs)</Text>}
        {f?.jobs.length === 0 && <Text dimColor>no jobs</Text>}
        {f?.jobs.map(one => (
          <Text>
            {one.dir.padEnd(20)} {String(one.runGpus).padStart(3)} / {one.pendJobs}
          </Text>
        ))}
        {f?.quota && <Text bold>Quota</Text>}
        {f?.quota && <Text>{f.quota}</Text>}
      </Box>
    )
  })
}
