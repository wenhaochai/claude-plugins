"""Write the template deck: one slide per layout, placeholder text, example numbers.

    python3 build_template.py OUT

OUT becomes a Slides deck folder (project/deck.json plus project/slides/<id>.html) that lint.py
and audit_render.py can check. Replace every [bracketed] string and every example number with
real, sourced data; the numbers only show the geometry.
"""
import datetime as _dt
import json
import os
import random
import sys

from deckkit import *

if len(sys.argv) != 2:
    sys.exit(__doc__)
OUT = os.path.abspath(sys.argv[1])
SL = os.path.join(OUT, 'project', 'slides')
os.makedirs(SL, exist_ok=True)
S = {}

# ---------------------------------------------------------------- cover
S['cover'] = cover('cover', 'Paper presentation · arXiv [id]', '[Paper title,<br>two lines at most]',
                   'Paper by [Author], [Month Year]', 'Presented by [Presenter]', '[Month Year]',
                   note='[Script] The question the paper asks, in one line.\n\n[讲稿] 一句话说论文问的问题。')

# ---------------------------------------------------------------- agenda
S['agenda'] = agenda('agenda', [('The paper', '[the method in a few words]'), ('[Part 2]', '[what the part covers]'),
                                ('[Part 3]', '[what the part covers]')], title='Three parts',
                     note='[Script] The parts, one sentence each.\n\n[讲稿] 每部分一句话。')

# ---------------------------------------------------------------- paper: first page and the question
body = f'''<div style="flex:1; display:flex; gap:72px; align-items:flex-start">
    {image('First page of [paper]: title, authors, abstract and Figure 1', 620, 645, extra=f'background:{WHITE}; border:1px solid {RULE}; box-shadow:0 4px 24px rgba(0,0,0,0.06)')}
    <div style="flex:1; display:flex; flex-direction:column; gap:12px; padding:24px 0 0 0">
      {label('Question')}
      <p style="font-size:36px; line-height:1.3; color:{INK}">[The question the paper asks, in one sentence]</p>
    </div>
  </div>'''
S['paper'] = slide('paper', 'Part 1 · The paper', '[Paper title]', body, 'Source: arXiv [id], [date]',
                   note='[Script] Where the data come from.\n[Script] The question the paper asks.\n\n[讲稿] 数据来自哪里；论文要回答的问题。')

# ---------------------------------------------------------------- method: a distribution with the kept band
heights = [360, 150, 59, 143, 91, 69, 103, 91, 78, 88, 135, 50, 74, 91, 40, 70, 72, 27, 67, 57]
bands = [(15, 460, 'Too hard, dropped: [n] items', False), (602, 460, 'Kept: [n] items', True), (1189, 460, 'Too easy, dropped: [n] items', False)]
axis = [(0, 80, '0%', 'left'), (457, 80, '30%', 'center'), (1127, 80, '70%', 'center'), (1584, 80, '100%', 'right')]
body = (histogram(heights, set(range(6, 14)), bands, axis)
        + f'\n  <p style="font-size:28px; color:{SOFT}">[What the x axis measures, over how many items]</p>\n  <div style="flex:1"></div>')
S['method'] = slide('method', 'Part 1 · The paper', 'Method', body, 'Source: [paper]; [how the numbers were computed]',
                    note='[Script] The method, one step per line.\n[Script] What the colors mean.\n\n[讲稿] 方法怎么做，图里的颜色是什么意思。')

# ---------------------------------------------------------------- results: fit plot and method comparison
rng = random.Random(7)
pts = [(x, min(max(x + rng.gauss(0, 0.035), 0.0), 0.8)) for x in (rng.uniform(0.03, 0.76) for _ in range(80))]
host, xrow = scatter(pts, notes=[('ρ = [0.99]', f'font-size:24px; color:{ACC}'), ('R² = [0.97]', f'font-size:24px; color:{SOFT}')],
                     aria='[Benchmark]: predicted versus full score, one dot per model')
comp = [('Ours', 0.94, 0.99, 0.87, True), ('Method A', 0.92, 0.98, 0.83, False), ('Method B', 0.88, 0.99, 0.54, False),
        ('Method C', 0.88, 0.98, 0.68, False), ('Method D', 0.86, 0.99, 0.56, False)]
body = f'''<div style="flex:1; display:flex; gap:72px">
    <div style="width:700px; display:flex; flex-direction:column; gap:8px">
      <p style="font-size:24px; font-weight:600; color:{INK}">One dot per [unit] on [Benchmark]</p>
      <p style="font-size:24px; color:{SOFT}; padding:8px 0 0 0">Predicted from the [n] kept items</p>
      {host}
      {xrow}
      <p style="width:500px; font-size:24px; color:{SOFT}; text-align:right">Full score on all [n] items</p>
    </div>
    <div style="flex:1; display:flex; flex-direction:column; gap:8px">
      <p style="font-size:24px; font-weight:600; color:{INK}">[Methods compared at the same budget]</p>
      <p style="font-size:24px; line-height:1.4; color:{SOFT}">Mean ρ; bar from worst to best</p>
      {range_rows(comp)}
    </div>
  </div>'''
S['results'] = slide('results', 'Part 1 · The paper', 'Results', body, 'Source: [paper, table and figure]', gap=28,
                     note="[Script] Left: the axes, what each dot is, and rho.\n[Script] Right: each method's mean and worst case.\n\n[讲稿] 左图：横轴、纵轴、每个点、ρ。右图：每种方法的平均和最差。")

# ---------------------------------------------------------------- index: weights, graders and a leaderboard
groups = [('[Category A] · 30%', [(15, INK), (10, GREY), (5, INK)], '[Eval A] 15 · [Eval B] 10 · [Eval C] 5'),
          ('[Category B] · 30%', [(15, INK), (10, GREY), (5, GREY)], '[Eval D] 15 · [Eval E] 10 · [Eval F] 5'),
          ('[Category C] · 20%', [(10, GREY), (10, GREY)], '[Eval G] 10 · [Eval H] 10'),
          ('[Category D] · 20%', [(10, GREY), (10, INK)], '[Eval I] 10 · [Eval J] 10')]
segs = [(0.35, BLUE, 'Tests and checks', '[Eval G], [Eval H], [Eval J], [Eval C]'), (0.40, ACC, '[One LLM grader]', '[Eval D], [Eval I], [Eval E], [Eval F]'),
        (0.25, RED_STRIPE, 'Judge panel', '[Eval A], [Eval B]')]
rows = [('[Model A]', '69.7', 69.7, 68.8, 70.6), ('[Model B]', '68.8', 68.8, 67.8, 69.9), ('[Model C]', '67.2', 67.2, 66.2, 68.2),
        ('[Model D]', '66.6', 66.6, 65.5, 67.7), ('[Model E]', '66.0', 66.0, 65.0, 67.1)]
body = f'''<div style="flex:1; display:flex; gap:56px">
    {composition(groups, 24, [(INK, 'private set, [45]% in total'), (GREY, 'public set')])}
    <div style="flex:1; display:flex; flex-direction:column; gap:24px">
      <div style="display:flex; flex-direction:column; gap:10px">
        {ctitle('Who grades the [n] evals')}
        {seg_bar(segs, bracket=(1, 2, '[65]% graded by LLMs'))}
      </div>
      {board('Top five models with ± 1 standard error', rows, 62, 72, (62, 64, 66, 68, 70, 72), 260, 788 - 260 - 16 - 30, 36)}
    </div>
  </div>'''
S['index'] = slide('index', 'Part 2 · [Part name]', '[Index] [version]', body, 'Source: [site], read [DD Mon YYYY]', gap=32,
                   note='[Script] What is in the index, and who grades it.\n[Script] The leader, then one strength and one problem.\n\n[讲稿] 组成和判分；第一名；一个好处、一个问题。')

# ---------------------------------------------------------------- topic intro: how it works, a real task, three scores
cards = [card('Task', big('[600]'), '[public items, how they split]', sub('[how many more are private]')),
         card('Agent', big('[47]'), '[what the agent works in]', sub('[the step or turn limit]')),
         card('Grading', big('[State]'), '[the only thing the grader reads]', sub('[what it ignores]')),
         card('Checks', big('[11]'), '[checks per task, median]', f'<div style="display:flex; flex-wrap:wrap; gap:8px">{pill("✓ objective", BLUE)}{pill("✕ guardrail", ACC)}</div>')]
example = checklist('[One real task] and its checks', '[where the rule the task depends on lives]',
                    ['[Check that must hold]', '[Check that must hold, with the exact strings]', '[Check that must hold]'],
                    ['[Thing that must not happen]', '[Thing that must not happen]', '[Thing that must not happen]'])
scores = hbars('[Model] on the same [n] runs', [('[Rule 1]', 90.4, GREY, '90%'), ('[Rule 2]', 69.5, ACC, '69.5%'), ('[Rule 3]', 41.2, INK, '41.2%')])
body = f'''{pipeline(cards)}
  <div style="display:flex; gap:64px">
    {example}
    {scores}
  </div>'''
S['topic-intro'] = slide('topic-intro', 'Part 3 · [Topic] · [Maker, Month Year]', 'Tasks and grading', body,
                         'Sources: [paper]; [leaderboard]; example task [id]', gap=32,
                         note='[Script] The four steps, one line each.\n[Script] The real task and its checks.\n[Script] The same runs under three scoring rules.\n\n[讲稿] 流程四步；真实例子的检查；同一批运行的三种算分。')

# ---------------------------------------------------------------- example: prompt, rubric, the output that trips the check
rub = rubric('Rubric for [the output]', [('Objective', 'body contains [string]'), ('Guardrail', f'body does not contain {hl("[string]")}')])
out = quote_card('[Run], [output]', f'[Output text with the tripped string] {hl("[string]")} [rest of the output]')
body = f'''<div style="flex:1; display:flex; gap:56px">
    <div style="width:780px; display:flex; flex-direction:column; gap:28px">{quote_card('Prompt, excerpt', '“… [the sentence of the prompt that matters] …”')}
      {rub}
    </div>
    <div style="flex:1; display:flex; flex-direction:column; gap:24px">{out}
      <p style="font-size:28px; line-height:1.4; color:{INK}">[How many runs failed on this check, and why the work was correct]</p>
    </div>
  </div>'''
S['example'] = slide('example', 'Part 3 · [Topic] · Example', '[Task name]', body, 'Source: [task id]; [where the runs come from]', gap=36,
                     note='[Script] What the prompt asks, and the right answer.\n[Script] What the check tests, and which runs fail it.\n\n[讲稿] prompt 要求什么，正确答案是什么；检查写了什么，哪些运行因此失败。')

# ---------------------------------------------------------------- summary
S['summary'] = summary('summary', [('The paper', '[What part 1 showed, one line]'), ('[Part 2]', '[What part 2 showed, one line]'),
                                   ('[Part 3]', '[What part 3 showed, one line]')],
                       '[One closing line]', note='[Script] One sentence per part, then the closing line.\n\n[讲稿] 每部分一句话，最后一句收尾。')

for sid, html in S.items():
    open(os.path.join(SL, f'{sid}.html'), 'w').write(html)
index = os.path.join(OUT, 'project', 'deck.json')
try:
    created = json.load(open(index))['createdOnFiles']      # a rebuild keeps the original creation record
except (OSError, ValueError, KeyError):
    created = {'v': 1, 'at': _dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
deck = {'v': 4, 'createdOnFiles': created, 'title': '[Deck title]', 'order': list(S),
        'sections': {'s0': {'description': 'Title and outline', 'start': 'cover'}, 's1': {'description': 'The paper', 'start': 'paper'},
                     's2': {'description': '[Part 2]', 'start': 'index'}, 's3': {'description': '[Part 3]', 'start': 'topic-intro'},
                     's4': {'description': 'Summary', 'start': 'summary'}},
        'faces': FACES, 'designSystems': []}
json.dump(deck, open(index, 'w'), ensure_ascii=False, indent=2)
print(f'wrote {len(S)} slides to {SL}')
