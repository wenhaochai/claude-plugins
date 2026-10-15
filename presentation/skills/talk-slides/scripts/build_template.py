"""Write the template deck: one slide per layout, placeholder text.

    python3 build_template.py OUT

OUT becomes a Slides deck folder (project/deck.json plus project/slides/<id>.html) that lint.py
and audit_render.py can check. Replace every [bracketed] string with real, sourced content.
"""
import datetime as _dt
import json
import os
import sys

from deckkit import *

if len(sys.argv) != 2:
    sys.exit(__doc__)
OUT = os.path.abspath(sys.argv[1])
SL = os.path.join(OUT, 'project', 'slides')
os.makedirs(SL, exist_ok=True)
S = {}

S['cover'] = cover('cover', '[Venue or occasion]', '[Talk title,<br>two lines at most]', '[One line on the question]',
                   '[Speaker]', '[Affiliation], [Month Year]',
                   note='[Script] The question of the talk, in one line.\n[讲稿] 一句话说这次报告的问题。')

S['part1'] = part('part1', 'Part 1', '[Part title]', '[What this part covers, in one line]', T_BLUE,
                  note='[Script] What this part covers.\n[讲稿] 这一部分讲什么。')

body = f'''{lede('[The one lead line of the slide]')}
  {image('[What the figure shows]', 1664, 520)}'''
S['figure'] = slide('figure', 'Part 1', '[Noun title for what is shown]', body, 'Source: [paper, figure]',
                    note='[Script] What the figure shows.\n[讲稿] 图里是什么。')

stats = ''.join(stat(f'[{n}]', '[What the number counts]', '[where it comes from]', accent=(i == 0)) for i, n in enumerate(('2.05x', '98')))
S['numbers'] = slide('numbers', 'Part 1', '[Noun title]', f'<div style="display:flex; gap:96px">{stats}</div>', 'Source: [where the numbers come from]',
                     note='[Script] The number that matters, and what it counts.\n[讲稿] 最重要的那个数字，以及它数的是什么。')

cols = ''.join(column(f'[Heading {i}]', '[One sentence on it]') for i in (1, 2, 3))
S['columns'] = slide('columns', 'Part 1', '[Noun title]', f'<div style="display:flex; gap:64px">{cols}</div>',
                     note='[Script] One line per column.\n[讲稿] 每栏一句。')

for sid, html in S.items():
    open(os.path.join(SL, f'{sid}.html'), 'w').write(html)
index = os.path.join(OUT, 'project', 'deck.json')
try:
    created = json.load(open(index))['createdOnFiles']      # a rebuild keeps the original creation record
except (OSError, ValueError, KeyError):
    created = {'v': 1, 'at': _dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
deck = {'v': 4, 'createdOnFiles': created, 'title': '[Deck title]', 'order': list(S),
        'sections': {'s0': {'description': 'Title', 'start': 'cover'}, 's1': {'description': '[Part 1]', 'start': 'part1'}},
        'faces': FACES, 'designSystems': []}
json.dump(deck, open(index, 'w'), ensure_ascii=False, indent=2)
print(f'wrote {len(S)} slides to {SL}')
