"""Template 23: log-log multi-line comparison with reference dashed line.

Use when: comparing scaling exponents across two settings against a known
reference (e.g. Chinchilla). Two solid lines + one dashed reference.
"""
import numpy as np
import matplotlib.pyplot as plt
from style import (apply_style, hue_ramp, header_legend, finalize_headers,
                   G_BLUE, REF_GREY, REF_DASH)

# Two series (<= 3): light/dark steps of one hue via hue_ramp
RAMP = hue_ramp(G_BLUE, 2)

apply_style()

C = np.logspace(18.5, 25, 100)

CURVES = {
    'a': dict(y=10 ** (np.log10(40) + 0.47 * (np.log10(C) - 18.5)),
              color=RAMP[1], linestyle='-',
              label=r'Modality A: $C^{0.47}$'),
    'b': dict(y=10 ** (np.log10(80) + 0.37 * (np.log10(C) - 18.5)),
              color=RAMP[0], linestyle='-',
              label=r'Modality B: $C^{0.37}$'),
    'ref': dict(y=10 ** (np.log10(20) + 0.49 * (np.log10(C) - 18.5)),
                color=REF_GREY,      linestyle=REF_DASH,
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
# line proxies: '-' solid, '--' reference dash
header_legend(ax, [(CURVES['a']['label'], CURVES['a']['color'], '-'),
                   (CURVES['b']['label'], CURVES['b']['color'], '-'),
                   (CURVES['ref']['label'], REF_GREY, '--')],
              ncol=1, legend_size=8)
finalize_headers(fig)
