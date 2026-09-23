"""Write the 14-slide template deck: one slide per layout, placeholder text, example numbers.

    python3 build_template.py [out_dir]      # default: ../template

The output is a Slides deck folder (project/deck.json plus project/slides/<id>.html) that the
audit scripts can render. Replace every [bracketed] string and every example number with real,
sourced data before publishing; the numbers only show the geometry.
"""
import datetime as _dt
import math
import json
import os
import random
import sys

from deckkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, '..', 'template')
SL = os.path.join(OUT, 'project', 'slides')
os.makedirs(SL, exist_ok=True)
S = {}

# ---------------------------------------------------------------- 1 cover
S['cover'] = cover('cover', 'Paper presentation · arXiv [id]', '[Paper title,<br>two lines at most]',
                   'Paper by [Author], [Month Year]', 'Presented by [Presenter]', '[Month Year]',
                   note=script(['[Script] One line on the question the paper asks.', '[Script] One line on what the other parts cover.'], ['[讲稿] 一句话说论文问的问题，再说后面几个部分讲什么。']))

# ---------------------------------------------------------------- 2 agenda
S['agenda'] = agenda('agenda', [('The paper', '[the method in a few words]'), ('[Part 2]', '[the idea in a few words]'),
                                ('[Part 3]', '[what the part covers]'), ('[Part 4]', '[what the part covers]')],
                     note=script(['[Script] The four parts, one sentence each.'], ['[讲稿] 分四部分，每部分一句话。']))

# ---------------------------------------------------------------- 3 paper: first-page screenshot and the question
body = f'''<div style="flex:1; display:flex; gap:72px; align-items:flex-start">
    {image('First page of [paper]: title, authors, abstract and Figure 1', 620, 645, extra=f'background:{WHITE}; border:1px solid {RULE}; box-shadow:0 4px 24px rgba(0,0,0,0.06)')}
    <div style="flex:1; display:flex; flex-direction:column; gap:48px; padding:24px 0 0 0">
      <div style="display:flex; flex-direction:column; gap:12px">
        {label('Question')}
        <p style="font-size:36px; line-height:1.3; color:{INK}">[The question the paper asks, in one sentence]</p>
      </div>
    </div>
  </div>'''
S['paper'] = slide('paper', 'Part 1 · The paper', '[Paper title]', body, 'Source: arXiv [id], [date]',
                   note=script(['[Script] Where the data come from.', '[Script] The question the paper asks, read from the slide.'], ['[讲稿] 数据来自哪里；论文要回答的问题。作者名不念。']))

# ---------------------------------------------------------------- 4 method: a distribution with the kept band
heights = [360, 150, 59, 143, 91, 69, 103, 91, 78, 88, 135, 50, 74, 91, 40, 70, 72, 27, 67, 57]
bands = [(15, 460, 'Too hard, dropped: [n] items', False), (602, 460, 'Kept: [n] items', True), (1189, 460, 'Too easy, dropped: [n] items', False)]
axis = [(0, 80, '0%', 'left'), (457, 80, '30%', 'center'), (1127, 80, '70%', 'center'), (1584, 80, '100%', 'right')]
body = (histogram(heights, set(range(6, 14)), bands, axis)
        + f'\n  <p style="font-size:28px; color:{SOFT}">[What the x axis measures, over how many items]</p>\n  <div style="flex:1"></div>')
S['method'] = slide('method', 'Part 1 · The paper', 'Method', body, 'Source: [paper]; [how the numbers were computed]',
                    note=script(['[Script] The method, one step per line.', '[Script] What each color means, and how many items are kept.'], ['[讲稿] 方法怎么做，图里每个颜色是什么，丢掉和保留的数量。']))

# ---------------------------------------------------------------- 5 results: fit plot and method comparison
rng = random.Random(7)
pts = []
for _ in range(80):
    x = rng.uniform(0.03, 0.76)
    pts.append((x, min(max(x + rng.gauss(0, 0.035), 0.0), 0.8)))
host, xrow = scatter(pts, notes=[('ρ = [0.99]', f'font-size:32px; font-weight:600; color:{ACC}'), ('R² = [0.97]', f'font-size:24px; color:{SOFT}')],
                     aria='[Benchmark]: predicted versus full score, one dot per model')
left = f'''<div style="width:700px; display:flex; flex-direction:column; gap:8px">
      <p style="font-size:24px; font-weight:600; color:{INK}">One dot per [unit] on [Benchmark]</p>
      <p style="font-size:24px; color:{SOFT}; padding:8px 0 0 0">Predicted from the [n] kept items</p>
      {host}
      {xrow}
      <p style="width:500px; font-size:24px; color:{SOFT}; text-align:right">Full score on all [n] items</p>
    </div>'''
comp = [('Ours', 0.94, 0.99, 0.87, True), ('Method A', 0.92, 0.98, 0.83, False), ('Method B', 0.88, 0.99, 0.54, False),
        ('Method C', 0.88, 0.98, 0.68, False), ('Method D', 0.86, 0.99, 0.56, False)]
right = f'''<div style="flex:1; display:flex; flex-direction:column; gap:8px">
      <p style="font-size:24px; font-weight:600; color:{INK}">[Methods compared at the same budget]</p>
      <p style="font-size:24px; line-height:1.4; color:{SOFT}">Mean ρ; bar from worst to best</p>
      {range_rows(comp)}
    </div>'''
body = f'''<div style="flex:1; display:flex; gap:72px">
    {left}
    {right}
  </div>'''
S['results'] = slide('results', 'Part 1 · The paper', 'Results', body, 'Source: [paper, table and figure]; left panel recomputed from the released data', gap=28,
                     note=script(['[Script] Left: the two axes, what each dot is, and rho.', "[Script] Right: each method's mean and worst case.", '[Script] One caveat, if it changes how to read the result.'], ['[讲稿] 左图：横轴、纵轴、每个点是什么，ρ 和 R²。右图：几种方法各自的平均和最差。注意事项放这里。']))

# ---------------------------------------------------------------- 6 concept: source figure plus a diverging bar chart
rows = [('[Item A]', 0.42), ('[Item B]', 0.37), ('[Item C]', 0.35), ('[Item D]', 0.33), ('[Item E]', -0.26), ('[Item F]', -0.28), ('[Item G]', -0.35)]
body = f'''<div style="flex:1; display:flex; gap:64px; align-items:flex-start">
    <div style="width:420px; display:flex; flex-direction:column; gap:8px">
      <p style="font-family:{SERIF}; font-size:48px; font-weight:500; line-height:1.1; color:{INK}">[First term]</p>
      <p style="font-size:24px; color:{SOFT}">[what the figure shows, with its headline number]</p>
      {image('[Source figure: what it plots]', 420, 525, extra=f'border:1px solid {RULE}')}
    </div>
    <div style="flex:1; display:flex; flex-direction:column; gap:8px">
      <p style="font-family:{SERIF}; font-size:48px; font-weight:500; line-height:1.1; color:{ACC}">+ [Second term]</p>
      <p style="font-size:24px; color:{SOFT}">[what the bars are]</p>
      {diverging(rows, 'toward [side A]', 'toward [side B]')}
    </div>
  </div>'''
S['concept'] = slide('concept', 'Part 2 · [Part name]', '[Source title, used as given]', body, 'Source: [author, venue, date]; figure [license]',
                     note=script(['[Script] What the left figure shows.', "[Script] What the bars show, and the source's sign convention."], ['[讲稿] 左边是什么，右边的条是什么；原文的正负号约定写在这里，图上只画大小和方向。']))

# ---------------------------------------------------------------- 7 index with a selection funnel, launch results and the official figure
stages = [(6627, 'Candidate pool'), (1311, 'Difficulty: [rule]'), (307, '[Screen]'), (100, '[Review]'), (82, '[Final step]')]
lead = [('[Model A] in [harness]', 23), ('[Model B] in [harness]', 17), ('[Model A] in [harness 2]', 16), ('[Model B] in [harness 2]', 13), ('[Model C] in [harness]', 11)]
brows = []
for nm, k in lead:
    p = k / 82
    z, n = 1.96, 82
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    brows.append((nm, f'{100 * p:.1f}%', 100 * p, 100 * (c - h), 100 * (c + h)))
board_html = board('Top five [entries] at launch with 95% intervals', brows, 0, 40, (0, 10, 20, 30, 40), 440, 870 - 440 - 16 - 30, 34,
                   tick_fmt=lambda t: f'{t}%', caption='[What the live leaderboard shows today]')
body = f'''<div style="flex:1; display:flex; gap:64px; align-items:stretch">
    <div style="flex:1; display:flex; flex-direction:column; justify-content:space-between">
      {funnel(stages)}
      {board_html}
    </div>
    {image('[Official figure: what it shows]', 730, 645, extra='background:#0A0A0A; border-radius:12px')}
  </div>'''
S['index-funnel'] = slide('index-funnel', 'Part 3 · [Part name]', '[Index A]', body, 'Source: [paper, table]; [site]; funnel bars on a log scale; Wilson 95% intervals',
                          note=script(['[Script] The rule at each step of the funnel.', '[Script] How to read the official figure.', '[Script] The leader, and how wide the intervals are.', '[Script] One strength and one problem.'], ['[讲稿] 筛选流程每一步的规则；右边官网图的读法；排行榜的第一名和区间。最后一个好处、一个问题。']))

# ---------------------------------------------------------------- 8 index with category weights, graders and a leaderboard without intervals
groups = [('[Category A] · 30%', [(15, INK), (10, GREY), (5, INK)], '[Eval A] 15 · [Eval B] 10 · [Eval C] 5'),
          ('[Category B] · 30%', [(15, INK), (10, GREY), (5, GREY)], '[Eval D] 15 · [Eval E] 10 · [Eval F] 5'),
          ('[Category C] · 20%', [(10, GREY), (10, GREY)], '[Eval G] 10 · [Eval H] 10'),
          ('[Category D] · 20%', [(10, GREY), (10, INK)], '[Eval I] 10 · [Eval J] 10')]
segs = [(0.35, BLUE, 'Tests and checks', '[Eval G], [Eval H], [Eval J], [Eval C]'), (0.40, ACC, '[One LLM grader]', '[Eval D], [Eval I], [Eval E], [Eval F]'),
        (0.25, RED_STRIPE, 'Judge panel', '[Eval A], [Eval B]: pairwise Elo')]
aa_rows = [('[Model A]', '57.6', 57.6, None, None), ('[Model B]', '53.4', 53.4, None, None), ('[Model C]', '52.7', 52.7, None, None),
           ('[Model D]', '48.1', 48.1, None, None), ('[Model E]', '47.5', 47.5, None, None)]
right = f'''<div style="flex:1; display:flex; flex-direction:column; gap:24px">
      <div style="display:flex; flex-direction:column; gap:10px">
        {ctitle('Who grades the ten evals')}
        {seg_bar(segs, bracket=(1, 2, '65% graded by LLMs'))}
        <p style="font-size:24px; line-height:1.3; color:{SOFT}">Panel: [Judge A], [Judge B] and [Judge C]</p>
      </div>
      {board('Top five models at their best setting', aa_rows, 40, 60, (40, 45, 50, 55, 60), 260, 788 - 260 - 16 - 30, 36)}
    </div>'''
body = f'''<div style="flex:1; display:flex; gap:56px">
    {composition(groups, 24, [(INK, 'private set, [45]% in total'), (GREY, 'public set')])}
    {right}
  </div>'''
S['index-graders'] = slide('index-graders', 'Part 3 · [Part name]', '[Index B] [version]', body, 'Source: [site], read [DD Mon YYYY]', gap=32,
                           note=script(['[Script] What is in the index, and the weights.', '[Script] Who grades each share.', '[Script] The leader, and how the top five were picked.', '[Script] One strength and one problem.'], ['[讲稿] 组成和权重；谁来判分；第一名，前五名怎么选的。最后一个好处、一个问题。']))

# ---------------------------------------------------------------- 9 index with a weight formula, a legend bar and a leaderboard with errors
groups = [('[Sector A] · 54%', [(351, INK), (351, INK)], '[Benchmark A] · [Benchmark B]'),
          ('[Sector B] · 38%', [(164, GREY), (164, INK), (164, INK)], '[Benchmark C] · [Benchmark D] · [Benchmark E]'),
          ('[Sector C] · 8%', [(53, INK), (53, GREY)], '[Benchmark F] · [Benchmark G]')]
lsegs = [(0.2523, BLUE, 'Tests', '[Benchmark C], [Benchmark E]'), (0.2703, MIX_STRIPE, 'Cell match or LLM rubric', '[Benchmark B]'),
         (0.4774, ACC, 'LLM judges or an LLM agent', '[Benchmark A], [Benchmark F], [Benchmark G], [Benchmark D]')]
vrows = [('[Model A]', '69.69', 69.69, 68.75, 70.63), ('[Model B]', '68.83', 68.83, 67.75, 69.91), ('[Model C]', '67.21', 67.21, 66.23, 68.19),
         ('[Model D]', '66.61', 66.61, 65.52, 67.70), ('[Model E]', '66.04', 66.04, 65.01, 67.07)]
right = f'''<div style="flex:1; display:flex; flex-direction:column; gap:30px">
      <div style="display:flex; flex-direction:column; gap:10px">
        {ctitle('Who grades the seven benchmarks')}
        {legend_bar(lsegs)}
      </div>
      {board('Top five models with ± 1 standard error', vrows, 62, 72, (62, 64, 66, 68, 70, 72), 270, 788 - 270 - 16 - 30, 40)}
    </div>'''
body = f'''<div style="flex:1; display:flex; gap:56px">
    {composition(groups, 1, [(INK, 'private set, [5] of [7]'), (GREY, 'public set')], gap=14, formula='([w_A] · [Sector A] + [w_B] · [Sector B] + [w_C] · [Sector C]) / [sum]')}
    {right}
  </div>'''
S['index-legend'] = slide('index-legend', 'Part 3 · [Part name]', '[Index C] [version]', body, 'Source: [site], read [DD Mon YYYY]', gap=32,
                          note=script(['[Script] The weight formula, and how much is private.', '[Script] Who grades each share.', '[Script] The leaders, and whether their error bars overlap.', '[Script] One strength and one problem.'], ['[讲稿] 权重公式；私有和公开；判分方式；前几名的误差带是否重叠。最后一个好处、一个问题。']))

# ---------------------------------------------------------------- 10 index fitted with a latent scale: curves, counts and intervals
series = [('[Easy]', 111, 0.0757, GREY), ('[Middle]', 136, 0.0699, SOFT), ('[Hard]', 175, 0.1526, ACC)]
curve_html = curves(series, 100, 190, (110, 130, 150, 170, 190), anchors=((130, '[Anchor A]', 150), (150, '[Anchor B]', 150)),
                    labels=((101, 92, 90, '[Easy]', GREY), (131, 186, 250, '[Middle benchmark]', SOFT), (172.5, 182, 170, '[Hard]<br>[benchmark]', ACC)),
                    aria='Fitted curves on one scale: an easy, a middle and a hard benchmark')
counts = ''.join(f'''<div style="display:flex; flex-direction:column; gap:4px">
          <p style="font-family:{SERIF}; font-size:44px; line-height:1; color:{INK}">{n}</p>
          <p style="font-size:24px; color:{SOFT}">{t}</p>
        </div>''' for n, t in [('[58]', 'benchmarks'), ('[268]', 'models, each with ≥ [4] scores'), ('[2,780]', 'scores')])
left = f'''<div style="width:820px; display:flex; flex-direction:column; gap:16px">
      <div style="display:flex; flex-direction:column; gap:12px">
        <p style="font-family:{SERIF}; font-style:italic; font-size:32px; line-height:1.3; color:{INK}">score = σ(slope × (capability − difficulty))</p>
        {curve_html}
      </div>
      <div style="display:flex; gap:64px">{counts}</div>
    </div>'''
erows = [('[Model A]', '166.6', 166.6, 163.0, 172.0), ('[Model B]', '165.0', 165.0, 161.6, 169.6), ('[Model C]', '163.6', 163.6, 160.6, 167.6),
         ('[Model D]', '162.7', 162.7, 160.0, 166.5), ('[Model E]', '162.4', 162.4, 159.2, 166.6)]
body = f'''<div style="flex:1; display:flex; gap:56px">
    {left}
    <div style="flex:1; display:flex; flex-direction:column; gap:28px">
      {board('Top five models with 90% intervals', erows, 155, 175, (155, 160, 165, 170, 175), 250, 788 - 250 - 16 - 36, 54)}
    </div>
  </div>'''
S['index-curves'] = slide('index-curves', 'Part 3 · [Part name]', '[Index D]', body, 'Source: [site], read [DD Mon YYYY]', gap=32,
                          note=script(['[Script] How the model works, in two or three lines.', '[Script] What the three real curves show.', '[Script] The two anchors of the scale.', '[Script] Whether the top intervals overlap.', '[Script] One strength and one problem.'], ['[讲稿] 模型怎么拟合；三条真实曲线各代表什么；刻度的锚点；前几名的区间是否重叠。最后一个好处、一个问题。']))

# ---------------------------------------------------------------- 11 topic intro: pipeline cards, a real example, three scores of one run set
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
S['topic-intro'] = slide('topic-intro', 'Part 4 · [Benchmark] · [Maker, Month Year]', 'Tasks and grading', body,
                         'Sources: [paper]; [leaderboard]; example task [id] from the public [version] set', gap=32,
                         note=script(['[Script] The four steps, one line each.', '[Script] The real task and its checks, without names from the task data.', '[Script] The same runs under three scoring rules.'], ['[讲稿] 流程四步；真实例子的检查，不念任务数据里的人名和团队名；同一批运行在三种算分下的结果。']))

# ---------------------------------------------------------------- 12 example with one output: prompt, rubric, the output that trips the check
rub = rubric('Rubric for [the output]', [('Objective', 'body contains <b>[string]</b>'), ('Guardrail', f'body does not contain {hl("[string]")}')])
left = f'''<div style="width:780px; display:flex; flex-direction:column; gap:28px">{quote_card('Prompt, excerpt', '“… [the sentence of the prompt that matters] …”')}
      {rub}
    </div>'''
out = quote_card('[Run], [output]', f'[Output text with the tripped string] {hl("[string]")} [rest of the output]', italic=False)
right = f'''<div style="flex:1; display:flex; flex-direction:column; gap:24px">{out}
      <p style="font-size:28px; line-height:1.4; color:{INK}">[How many runs failed on this check, and why the work was correct]</p>
    </div>'''
S['example-1'] = slide('example-1', 'Part 4 · [Benchmark] · Example 1', '[Task name]', f'''<div style="flex:1; display:flex; gap:56px">
    {left}
    {right}
  </div>''', 'Source: [task id], [benchmark version]; [where the runs come from]', gap=36,
                       note=script(['[Script] What the prompt asks, and the right answer.', '[Script] What the check tests, and which runs fail it.'], ['[讲稿] prompt 要求什么，正确答案是什么，检查写了什么，哪几个运行因此失败。']))

# ---------------------------------------------------------------- 13 example with several runs: context, rubric, what each run produced
left = f'''<div style="width:780px; display:flex; flex-direction:column; gap:28px">{quote_card('Context', '[The fact in the task data that decides the right answer]', italic=False)}
      {rub}
    </div>'''
right = outputs('What the runs produced', [('[Run A]', f'“[quoted output with] {hl("[string]")} [in it]”'), ('[Run B]', f'“[quoted output with] {hl("[string]")} [in it]”')],
                '[How the check scored these runs, and why the work was correct]')
S['example-2'] = slide('example-2', 'Part 4 · [Benchmark] · Example 2', '[Task name]', f'''<div style="flex:1; display:flex; gap:56px">
    {left}
    {right}
  </div>''', 'Source: [task id], [benchmark version]; [where the runs come from]', gap=36,
                       note=script(['[Script] The fact in the data that decides the answer.', '[Script] What the check tests.', '[Script] What the runs wrote, and why they failed.'], ['[讲稿] 数据里决定正确答案的那条信息；检查写了什么；每个运行写了什么、为什么被判错。']))

# ---------------------------------------------------------------- 14 summary
S['summary'] = summary('summary', [('The paper', '[What part 1 showed, one line]'), ('[Part 2]', '[What part 2 showed, one line]'),
                                   ('[Part 3]', '[What part 3 showed, one line]'), ('[Part 4]', '[What part 4 showed, one line]')],
                       '[One closing line: what to report or do beyond the headline number]', note=script(['[Script] One sentence per part.', '[Script] One closing line.'], ['[讲稿] 每部分一句话，最后一句收尾。']))

order = list(S)
for sid, html in S.items():
    open(os.path.join(SL, f'{sid}.html'), 'w').write(html)
index = os.path.join(OUT, 'project', 'deck.json')
try:
    created = json.load(open(index))['createdOnFiles']      # a rebuild keeps the original creation record
except (OSError, ValueError, KeyError):
    created = {'v': 1, 'at': _dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
deck = {'v': 4, 'createdOnFiles': created,
        'title': '[Deck title]', 'order': order,
        'sections': {'s0': {'description': 'Title and outline', 'start': 'cover'}, 's1': {'description': 'The paper', 'start': 'paper'},
                     's2': {'description': '[Part 2]', 'start': 'concept'}, 's3': {'description': '[Part 3]', 'start': 'index-funnel'},
                     's4': {'description': '[Part 4]', 'start': 'topic-intro'}, 's5': {'description': 'Summary', 'start': 'summary'}},
        'faces': FACES, 'designSystems': []}
json.dump(deck, open(index, 'w'), ensure_ascii=False, indent=2)
print(f'wrote {len(order)} slides to {SL}')
