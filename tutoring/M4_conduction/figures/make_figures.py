"""The drawings of module M4.

They live here, beside the notebook, rather than inside it: the plotting code is long,
teaches nothing and made the notebook unreadable on the repository page. The notebook
shows the resulting images; this script is the only owner of them.

    python3 make_figures.py

writes the PNGs the notebook embeds into this folder. If NDT_COURSE_NOTES_FIGURES points
at a directory it also writes the PDF versions there.

File names carry the prefix `04_`, a figure numbering independent of the module number.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Wedge, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
NOTES = os.environ.get("NDT_COURSE_NOTES_FIGURES", "")
FILM, SOLID, INS, TPROF = "0.86", "0.62", "0.80", "tab:red"


def save(fig, name):
    fig.savefig(os.path.join(HERE, name + ".png"), dpi=110, bbox_inches="tight")
    if os.path.isdir(NOTES):
        fig.savefig(os.path.join(NOTES, name + ".pdf"), bbox_inches="tight")
    plt.close(fig)


# One layer stack for both panels, so the two pictures describe the same wall.
# (label, resistance per unit area in the plane case, colour, hatch)
LAYERS = [("inner film\n$h_1$", 1/5000.0, FILM, "///"),
          ("steel\n$t,\\ k$",   0.05/48.0, SOLID, None),
          ("insulation\n$t_{ins},\\ k_{ins}$", 0.04/0.85, INS, None),
          ("outer film\n$h_2$", 1/25.0,   FILM, "///")]


def plane_wall(ax):
    """Same area everywhere, so R = t/kA and U needs no reference surface."""
    R = np.array([r for _, r, _, _ in LAYERS]); frac = R/R.sum()
    T1, T2 = 300.0, 40.0
    widths = [0.10, 0.34, 0.28, 0.10]                    # drawn thickness, not to scale
    x = 0.16
    xs, Ts = [x], [T1]
    for (lab, _, col, hat), w, f in zip(LAYERS, widths, frac):
        ax.add_patch(Rectangle((x, 0.28), w, 0.44, fc=col, ec="0.3", lw=1.0, hatch=hat))
        ax.text(x + w/2, 0.20, lab, fontsize=8.5, ha="center", va="top")
        x += w; xs.append(x); Ts.append(Ts[-1] - f*(T1 - T2))
    ax.plot(xs, 0.30 + 0.40*(np.array(Ts) - T2)/(T1 - T2), color=TPROF, lw=2.2,
            marker="o", ms=3.5, zorder=5)
    ax.text(0.06, 0.74, "$T_{b,1}$", color=TPROF, fontsize=10)
    ax.text(x + 0.02, 0.30, "$T_{b,2}$", color=TPROF, fontsize=10)
    ax.text(0.50, 0.86, "same area through every layer", fontsize=9.5, ha="center",
            style="italic")
    ax.text(0.50, 0.06,
            r"$R_{tot}=\dfrac{1}{h_1}+\dfrac{t}{k}+\dfrac{t_{ins}}{k_{ins}}"
            r"+\dfrac{1}{h_2}$,      $U = 1/R_{tot}$", fontsize=10.5, ha="center")
    ax.set_title("plane wall", fontsize=12, fontweight="bold")
    ax.set_xlim(0, 1.05); ax.set_ylim(0, 0.98); ax.axis("off")


def cylindrical_wall(ax):
    """Every layer sits at a different radius, so its area differs: R gains a logarithm
    and U is meaningless until a reference surface is named."""
    radii = [0.30, 0.38, 0.62, 0.86, 0.94]
    for (lab, _, col, hat), r0, r1 in zip(LAYERS, radii[:-1], radii[1:]):
        ax.add_patch(Wedge((0, 0), r1, 0, 360, width=r1 - r0, fc=col, ec="0.3",
                           lw=1.0, hatch=hat))
    ax.add_patch(Wedge((0, 0), radii[0], 0, 360, width=radii[0], fc="w", ec="0.3", lw=1.0))
    # Radius callouts dropped BELOW the disc, so no label sits on a grey ring.
    for r, nm in zip(radii, ("$r_1$", "", "$r_3$", "", "$r_5$")):
        if not nm:
            continue
        ax.plot([r, r], [0, -1.08], color="0.5", lw=0.8, ls=":")
        ax.plot([0, r], [-1.08, -1.08], color="0.5", lw=0.8, ls=":")
        ax.text(r, -1.20, nm, fontsize=10, ha="center")
    ax.plot(0, 0, "o", color="0.3", ms=3.5)
    ax.text(0, 1.06, "each layer a different area", fontsize=9.5, ha="center",
            style="italic")
    ax.text(0, -1.42, r"$R_i=\dfrac{\ln(r_{i+1}/r_i)}{2\pi k_i L}$,     "
                      r"$\dfrac{1}{U_{ref}A_{ref}}=\sum_i\dfrac{1}{U_iA_i}$",
            fontsize=10.5, ha="center")
    ax.text(0, -1.66, "a $U$ without its reference surface is meaningless",
            fontsize=9.5, ha="center", color=TPROF)
    ax.set_title("cylindrical wall", fontsize=12, fontweight="bold")
    ax.set_xlim(-1.15, 1.15); ax.set_ylim(-1.78, 1.15); ax.set_aspect("equal")
    ax.axis("off")


def main():
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.0),
                             gridspec_kw={"width_ratios": [1.25, 1.0]})
    plane_wall(axes[0]); cylindrical_wall(axes[1])
    fig.suptitle("The same four layers in series. The geometry changes what a resistance "
                 "is, not how they add.", fontsize=11.5, y=1.00)
    plt.tight_layout()
    save(fig, "04_resistance_network")


if __name__ == "__main__":
    main()
