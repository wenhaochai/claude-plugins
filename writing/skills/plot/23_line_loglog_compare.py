"""Template 23: log-log multi-line comparison with reference dashed line.

Use when: comparing scaling exponents across two settings against a known
reference (e.g. Chinchilla). Two solid lines + one dashed reference.
"""
import numpy as np
import matplotlib.pyplot as plt
from style import apply_style, paper, G_BLUE, G_RED, G_GREY

apply_style()

C = np.logspace(18.5, 25, 100)

CURVES = {
    'a': dict(y=10 ** (np.log10(40) + 0.47 * (np.log10(C) - 18.5)),
              color=paper(G_BLUE), linestyle='-',
              label=r'Modality A: $C^{0.47}$'),
    'b': dict(y=10 ** (np.log10(80) + 0.37 * (np.log10(C) - 18.5)),
              color=paper(G_RED),  linestyle='-',
              label=r'Modality B: $C^{0.37}$'),
    'ref': dict(y=10 ** (np.log10(20) + 0.49 * (np.log10(C) - 18.5)),
                color=G_GREY,        linestyle='--',
                label=r'Reference: $C^{0.49}$'),
}

fig, ax = plt.subplots(figsize=(4.0, 3.0), constrained_layout=True)

for s in CURVES.values():
    ax.plot(C, s['y'], color=s['color'], linestyle=s['linestyle'],
            linewidth=2.0, label=s['label'])

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Compute (FLOPs)')
ax.set_ylabel('Optimal Parameters (M)')
ax.set_title(r'$N_{\mathrm{opt}}$ Comparison')
ax.legend(loc='upper left')
ax.grid(which='both', linestyle='--', alpha=0.4)
