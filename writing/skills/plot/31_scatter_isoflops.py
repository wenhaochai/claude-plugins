"""Template 31: IsoFLOPs scatter — multiple parabolic curves with fits.

Use when: visualizing that for each compute budget there's an optimal model
size (the parabolic minimum). Each color = one budget; scatter + dotted
parabola fit. Marker size grows with parameter count (paper convention).
"""
import numpy as np
import matplotlib.pyplot as plt
from style import apply_style, paper, G_BLUE, G_GREEN, G_YELLOW, G_RED, G_PURPLE

apply_style()
rng = np.random.default_rng(0)

COMPUTE_LEVELS = [6e18, 6e19, 3e20, 6e20, 1e21]
COMPUTE_LABELS = ['6e18', '6e19', '3e20', '6e20', '1e21']
COMPUTE_COLORS = [paper(c) for c in (G_BLUE, G_GREEN, G_YELLOW, G_RED, G_PURPLE)]


def isoflop_curve(N, c_level):
    log_N = np.log10(N)
    rel = np.log10(c_level / 6e18)
    log_n_star = 8.4 + 0.47 * rel
    floor = 3.70 - 0.39 * rel
    return floor + 0.55 * (log_N - log_n_star) ** 2


fig, ax = plt.subplots(figsize=(5.0, 3.6), constrained_layout=True)

N_dense = np.logspace(8.0, 10.0, 80)
log_n_min, log_n_max = 8.2, 9.7
n_pts = 14
log_N_pts = np.linspace(log_n_min, log_n_max, n_pts)
N_pts = 10 ** log_N_pts

for c, color, label in zip(COMPUTE_LEVELS, COMPUTE_COLORS, COMPUTE_LABELS):
    loss_pts = isoflop_curve(N_pts, c)
    sizes = 12 + 70 * (log_N_pts - log_n_min) / (log_n_max - log_n_min)
    ax.scatter(N_pts, loss_pts + rng.normal(0, 0.012, n_pts),
               s=sizes, color=color, alpha=0.9, edgecolors='none', label=label)
    ax.plot(N_dense, isoflop_curve(N_dense, c),
            color=color, linestyle=':', linewidth=1.1, alpha=0.85)

ax.set_xscale('log')
ax.set_xlabel('Parameters')
ax.set_ylabel('Validation Loss')
ax.set_xticks([1e8, 3e8, 1e9, 3e9, 1e10])
ax.set_xticklabels(['100M', '300M', '1B', '3B', '10B'])
ax.set_ylim(2.65, 4.15)
ax.set_title('IsoFLOPs: Modality A')
ax.legend(fontsize=9, loc='upper right')
ax.grid(linestyle='--', alpha=0.4)
