export type GpuStatus = {
  at: number
  mine: number
  pendJobs: number
  pendGpus: number
  rank: number
  users: number
  used: number
  total: number
  free: number
  top: [string, number][]
}

export type FleetSession = { name: string; last: string }
export type FleetJobs = { dir: string; runGpus: number; pendJobs: number }

export type Fleet = {
  at: number
  sessions: FleetSession[]
  jobs: FleetJobs[]
  quota: string
}

declare module 'claude-code' {
  interface PluginState {
    'della-gpu': { status: GpuStatus | null; fleet: Fleet | null; isHidden: boolean }
  }
}
