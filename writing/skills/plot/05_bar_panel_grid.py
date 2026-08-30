"""Template 05: compact small-multiples bar grid (2x3 telemetry panel),
announcement-chart look. Use when: summarizing many categorical
distributions of one system in a single figure — each panel is a small
value-labeled bar chart; the first panel adds a twin log-scale line for a
second metric. Fonts step down to the dense-grid band (Principle 9); more
than 3 bars per panel -> distinct hues would shout, so panels reuse one
4-step ordered ramp read off the axis (legend-less encoding).
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

from style import (apply_style, clean_axes, finalize_headers,
                   G_BLUE, INK, darken, family_4)

apply_style()

ramp = family_4(G_BLUE)[::-1]        # dark -> light, rank order
edges = [darken(c, 0.2) for c in ramp]
stroke_white = [pe.withStroke(linewidth=2.0, foreground='white')]

# One (title, labels, values, value_label) block per panel.
PANELS = [
    ('Sessions by Level', ['L0', 'L1', 'L2', 'L3+'],
     [2, 2903, 2551, 1110], '{v:,}'),
    ('Interaction Modality', ['Mode\nA', 'Mode\nB', 'Mode\nC', 'Mode\nD'],
     [28.0, 57.2, 9.9, 4.9], '{v:.1f}%'),
    ('Message Direction', ['Up', 'Down', 'Intra', 'Cross'],
     [41.2, 36.5, 19.7, 2.6], '{v:.1f}%'),
    ('Distortion Types', ['Type\nA', 'Type\nB', 'Type\nC', 'Type\nD'],
     [0.36, 0.11, 0.11, 0.03], '{v:.2f}%'),
    ('Resolution Mechanisms', ['Mech\nA', 'Mech\nB', 'Mech\nC', 'Mech\nD'],
     [58.1, 21.4, 12.3, 8.2], '{v:.1f}%'),
    ('Dispute Triggers', ['Trig\nA', 'Trig\nB', 'Trig\nC', 'Trig\nD'],
     [64.0, 18.5, 10.2, 7.3], '{v:.1f}%'),
]
line_metric = [64978, 371, 178, 98]   # twin log-line on the first panel

fig, axes = plt.subplots(2, 3, figsize=(6.85, 3.1), constrained_layout=True)

for ax, (title, labels, vals, fmt) in zip(axes.flat, PANELS):
    x = np.arange(len(labels))
    bars = ax.bar(x, vals, width=0.5, color=ramp, edgecolor=edges,
                  linewidth=0.8, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
                ' ' + fmt.format(v=v), ha='center', va='bottom',
                fontsize=6.2, color=INK, path_effects=stroke_white)
    ax.set_xticks(x, labels, fontsize=6.2, linespacing=0.85)
    ax.tick_params(labelsize=7)
    ax.set_ylim(0, max(vals) * 1.28)
    ax.set_title(title, fontsize=8.2, pad=5)

# twin log-scale line on the first panel (second metric per category)
ax0 = axes.flat[0]
tw = ax0.twinx()
tw.set_yscale('log')
tw.plot(np.arange(len(line_metric)), line_metric, color=darken(ramp[0], 0.2),
        marker='o', markersize=3.2, linewidth=1.2, zorder=4)
tw.set_ylabel('Metric B (log)', fontsize=7)
tw.tick_params(labelsize=6.2)
clean_axes(tw)
tw.spines['right'].set_visible(True)
tw.spines['right'].set_color(INK)

finalize_headers(fig)
