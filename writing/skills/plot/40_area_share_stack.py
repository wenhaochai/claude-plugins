"""Template 40: 100%-stacked share-over-time area (streamgraph-style) with
direct in-band labels, announcement-chart look. Use when: a categorical
mix evolves over a run and the SHARES are the story — bands sum to 100%,
each band labeled inside itself at its widest point (no legend needed);
4 ordered bands use one hue's `family_4`, ink seams keep adjacent
bands separable.
"""
import numpy as np
import matplotlib.pyplot as plt

from style import apply_style, finalize_headers, G_BLUE, INK, family_4

apply_style()

rng = np.random.default_rng(5)
categories = ['Category A', 'Category B', 'Category C', 'Category D']
days = np.linspace(0, 50, 250)

# Placeholder shares: smooth random walks, normalized to 100% per x.
raw = [np.abs(np.convolve(rng.normal(1, 0.35, 250), np.ones(40) / 40,
                          mode='same')) + 0.15 for _ in categories]
raw[0] *= np.linspace(1.6, 0.9, 250)     # give band A a visible drift
raw[3] *= np.linspace(0.7, 1.4, 250)
shares = 100 * np.array(raw) / np.sum(raw, axis=0)

colors = family_4(G_BLUE)[::-1]   # darkest at the bottom

fig, ax = plt.subplots(figsize=(5.8, 3.0), constrained_layout=True)

ax.stackplot(days, shares, colors=colors, alpha=0.92,
             edgecolor=INK, linewidth=0.6, zorder=2)

# direct label inside each band at the x where the band is widest
cum = np.vstack([np.zeros_like(days), np.cumsum(shares, axis=0)])
for i, cat in enumerate(categories):
    j = int(np.argmax(shares[i][25:-25])) + 25    # stay off the edges
    y_mid = (cum[i][j] + cum[i + 1][j]) / 2
    light_band = i >= len(categories) / 2         # light bands get ink text
    ax.text(days[j], y_mid, cat, ha='center', va='center', fontsize=8.5,
            fontweight='bold', color=INK if light_band else 'white', zorder=5)

ax.set_xlim(0, 50)
ax.set_ylim(0, 100)
ax.set_xlabel('Run Days')
ax.set_ylabel('Share (%)')
ax.set_title('Category Mix over the Run')

finalize_headers(fig)
