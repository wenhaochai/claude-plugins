"""Template 43: taxonomy pill-table figure, announcement-chart look.
Use when: a categorized checklist (failure modes, criteria, rubric rows)
needs each row spanning the lifecycle stages it applies to, plus 1-2
right-aligned metric columns — light grey pills on an invisible axes,
grouped under bold category headings. A drawn table, not a chart: all
geometry in axes coords.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from style import apply_style, INK

apply_style()

PILL_BG, PILL_EDGE = '#f1f3f4', '#dadce0'

STAGES = ['Stage A', 'Stage B', 'Stage C']
METRICS = ['% Units', '% Steps']
# category -> rows; each row = (name, (first_stage, last_stage), m1, m2)
CATEGORIES = [
    ('Category 1: First Group of Modes (62% of total)', [
        ('1.1 Mode Alpha', (0, 1), 33.9, 4.1),
        ('1.2 Mode Beta', (0, 1), 19.5, 3.2),
        ('1.3 Mode Gamma', (1, 1), 5.5, 0.2),
    ]),
    ('Category 2: Second Group of Modes (27% of total)', [
        ('2.1 Mode Delta', (0, 1), 20.4, 1.5),
        ('2.2 Mode Epsilon', (1, 1), 4.2, 0.2),
        ('2.3 Mode Zeta', (0, 2), 2.6, 0.1),
    ]),
    ('Category 3: Third Group of Modes (11% of total)', [
        ('3.1 Mode Eta', (1, 2), 6.8, 0.3),
        ('3.2 Mode Theta', (2, 2), 6.6, 0.7),
    ]),
]

fig, ax = plt.subplots(figsize=(5.5, 3.0), constrained_layout=True)
ax.set_xlim(0, 1)
ax.axis('off')

# column geometry: stages block (left) + metrics block (right)
L, R, MAJOR_GAP, COL_GAP, STAGE_RATIO = 0.012, 0.988, 0.014, 0.008, 0.78
avail = R - L - MAJOR_GAP
stage_w = (avail * STAGE_RATIO - 2 * COL_GAP) / 3
metric_w = (avail * (1 - STAGE_RATIO) - COL_GAP) / 2
stage_x = [(L + i * (stage_w + COL_GAP),
            L + i * (stage_w + COL_GAP) + stage_w) for i in range(3)]
m0 = L + avail * STAGE_RATIO + MAJOR_GAP
metric_x = [(m0, m0 + metric_w), (m0 + metric_w + COL_GAP, R)]

def pill(x0, y0, w, h, **kw):
    ax.add_patch(FancyBboxPatch(
        (x0, y0), w, h, boxstyle='round,pad=0,rounding_size=0.006',
        linewidth=0.75, zorder=3, **kw))

# header row
HDR_H, y = 0.044, 0.982 - 0.044
for (x0, x1), name in zip(stage_x + metric_x, STAGES + METRICS):
    pill(x0, y, x1 - x0, HDR_H, facecolor=PILL_BG, edgecolor=PILL_EDGE)
    ax.text((x0 + x1) / 2, y + HDR_H / 2, name, ha='center', va='center',
            fontsize=8.2, fontweight='bold', color=INK, zorder=5)

# category blocks
ROW_H, ROW_GAP, TITLE_GAP, BLOCK_GAP = 0.055, 0.014, 0.038, 0.062
top = y
for title, rows in CATEGORIES:
    ty = top - (TITLE_GAP if top == y else BLOCK_GAP)
    ax.text(L, ty, title, ha='left', va='center', fontsize=8.2,
            fontweight='bold', color=INK, zorder=4)
    py = ty - TITLE_GAP - ROW_H / 2
    for name, (s0, s1), m1, m2 in rows:
        x0, x1 = stage_x[s0][0], stage_x[s1][1]
        pill(x0, py - ROW_H / 2, x1 - x0, ROW_H,
             facecolor=PILL_BG, edgecolor=PILL_EDGE)
        ax.text(x0 + 0.008, py, name, ha='left', va='center',
                fontsize=7.6, fontweight='bold', color=INK, zorder=4)
        for (mx0, mx1), val, unit in zip(metric_x, (m1, m2), ('%', '%')):
            ax.text(mx1 - 0.010, py, f'{val:.1f}{unit}', ha='right',
                    va='center', fontsize=7.4, fontweight='bold',
                    color=INK, zorder=4)
        top = py - ROW_H / 2
        py -= ROW_H + ROW_GAP

ax.set_ylim(top - 0.01, 1.0)
