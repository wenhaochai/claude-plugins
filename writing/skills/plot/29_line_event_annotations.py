"""Template 29: dual-panel smoothed trajectory with pointed event
annotations, announcement-chart look. Use when: the same derived ratio is
tracked over two runs and specific moments need calling out — one deep
line per panel (same hue both panels), a red annotation arrow marks the
event; annotation red is `G_RED` at the medium tier, reserved for the
callout only.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

from style import apply_style, finalize_headers, G_BLUE, G_RED, apply_tier, twotone

apply_style()

rng = np.random.default_rng(11)
dark, _ = twotone(G_BLUE, 'medium')
accent = apply_tier(G_RED, 'medium')

def trajectory(n, peak_at, peak, drop_at):
    """Placeholder ratio series: ramp to a peak, then decay past an event."""
    t = np.linspace(0, 1, n)
    y = peak * np.exp(-((t - peak_at) / 0.28) ** 2) + rng.normal(0, 0.08, n)
    y[t > drop_at] *= np.linspace(1, 0.15, (t > drop_at).sum())
    return gaussian_filter1d(np.abs(y), sigma=2.0)

PANELS = [  # (title, max_days, event_day, event_y, label_xy)
    ('Run A', 50, 36.0, 0.45, (21.0, 1.15)),
    ('Run B', 35, 26.0, 0.16, (13.0, 0.45)),
]
ymaxes = [2.5, 0.8]

fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.4), constrained_layout=True)

for ax, (title, max_d, ev_x, ev_y, label_xy), ymax in zip(axes, PANELS, ymaxes):
    days = np.linspace(0, max_d, 100)
    ax.plot(days, trajectory(100, 0.45, ymax * 0.75, 0.72),
            color=dark, linewidth=1.8, zorder=4)
    ax.annotate('Event label', xy=(ev_x, ev_y), xytext=label_xy,
                arrowprops=dict(arrowstyle='->', color=accent, lw=1.2,
                                shrinkA=3, shrinkB=4,
                                connectionstyle='arc3,rad=-0.08'),
                fontsize=8.5, fontweight='bold', color=accent, zorder=10)
    ax.set_xlim(0, max_d)
    ax.set_ylim(0, ymax)
    ax.set_xlabel('Run Days')
    ax.set_ylabel('Metric A Ratio')
    ax.set_title(title, fontsize=10.5)

finalize_headers(fig)
