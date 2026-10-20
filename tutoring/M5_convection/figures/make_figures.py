"""The drawings of module M5.

They live here, beside the notebook, rather than inside it: the plotting code is long,
teaches nothing and made the notebook unreadable on the repository page. The notebook
shows the resulting images; this script is the only owner of them.

    python3 make_figures.py

writes the PNGs the notebook embeds into this folder. If NDT_COURSE_NOTES_FIGURES points
at a directory it also writes the PDF versions there.

File names carry the prefix `04_` shared with the conduction drawings.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
NOTES = os.environ.get("NDT_COURSE_NOTES_FIGURES", "")
WALL, FLUID, TCOL, UCOL = "0.55", "#eaf2fb", "tab:red", "tab:blue"


def save(fig, name, png=True, pdf=True):
    if png:
        fig.savefig(os.path.join(HERE, name + ".png"), dpi=110, bbox_inches="tight")
    if pdf and os.path.isdir(NOTES):
        fig.savefig(os.path.join(NOTES, name + ".pdf"), bbox_inches="tight")
    plt.close(fig)


# Symbols: the notebook writes h_s, T_s, T_b; the PDF variant uses h, T_w, T_b, k_l.
SYM_NB = dict(h="h_s", w="T_s", b="T_b", k="k")
SYM_NOTES = dict(h="h", w="T_w", b="T_b", k="k_l")


def boundary_layer(ax, sym=SYM_NB):
    """Internal flow heated by the wall: the wall, the profile across half the channel, and
    the three temperatures that get confused - wall, bulk and centreline. Velocity is drawn
    with arrows because it is a vector; temperature is a curve, because it is not. The wall
    is the hottest point and T falls into the fluid; the bulk lies between wall and
    centreline."""
    H = 1.0
    y = np.linspace(0, H, 500)
    u = 1 - (1 - y/H)**2                       # laminar-like, so the weighting is visible
    T = (1 - y/H)**2                           # 1 at the heating wall, 0 on the centreline
    Tb = float(np.trapezoid(u*T, y)/np.trapezoid(u, y))   # bulk: velocity-weighted average
    h, w, b, k = (sym[c] for c in "hwbk")

    ax.add_patch(Rectangle((-0.30, -0.24), 1.86, 0.24, fc=WALL, ec="k", lw=1.0, hatch="///"))
    ax.text(-0.25, -0.12, "heated wall", fontsize=8.5, va="center", color="k",
            bbox=dict(fc="white", ec="none", pad=1))
    ax.add_patch(Rectangle((-0.30, 0), 1.86, H, fc=FLUID, ec="none"))
    ax.plot([-0.30, 1.56], [H, H], color="0.45", lw=1.0, ls="-.")
    ax.text(-0.28, H + 0.04, "centreline", fontsize=8, color="0.35")

    # velocity, as arrows
    for yy in np.linspace(0.05, H, 9):
        v = np.interp(yy, y, u)
        ax.add_patch(FancyArrowPatch((-0.22, yy), (-0.22 + 0.60*v, yy), arrowstyle="-|>",
                                     mutation_scale=8, color=UCOL, lw=1.0, alpha=0.7))
    ax.plot(-0.22 + 0.60*u, y, color=UCOL, lw=2.0)
    ax.text(0.30, 0.30, r"$u(y)$", color=UCOL, fontsize=12)

    # temperature, as a curve: horizontal position is T, from the centreline value at xT
    xT, sc = 0.74, 0.62
    ax.plot(xT + sc*T, y, color=TCOL, lw=2.4)
    ax.fill_betweenx(y, xT, xT + sc*T, color=TCOL, alpha=0.07)
    ax.text(xT + 0.20, 0.55, r"$T(y)$", color=TCOL, fontsize=12)
    m = (T[4] - T[0])/(y[4] - y[0])             # slope at the wall, dT/dy < 0
    ys = np.linspace(0, 0.35, 2)
    ax.plot(xT + sc*(1 + m*ys), ys, color=TCOL, lw=1.0, ls=":")
    ax.annotate("the slope at the wall is the flux:\n" + rf"$q'' = -{k}\,\partial T/\partial y|_w$",
                xy=(xT + sc*0.93, 0.03), xytext=(1.50, 0.42), fontsize=8.5, color=TCOL,
                arrowprops=dict(arrowstyle="->", color=TCOL, lw=0.8))

    # the three temperatures, as vertical marks along the T axis
    yt = 1.10
    for val, lab, sty, ha in ((1.0, rf"${w}$ wall", "-", "center"), (Tb, rf"${b}$ bulk", "--", "left"),
                              (0.0, "centreline ", "-.", "right")):
        ax.plot([xT + sc*val]*2, [0, yt - 0.03], color=TCOL, lw=0.8, ls=sty, alpha=0.8)
        ax.text(xT + sc*val, yt, lab, fontsize=9, ha=ha, color=TCOL)
    ax.annotate("", xy=(xT + sc*1.0, 0.86), xytext=(xT + sc*Tb, 0.86),
                arrowprops=dict(arrowstyle="<|-|>", color=TCOL, lw=1.1))
    ax.text(xT + sc*(1 + Tb)/2, 0.89, rf"${w}-{b}$", fontsize=9, color=TCOL, ha="center")

    ax.text(0.62, -0.40, rf"${h}$ is defined by  $q'' = {h}\,({w} - {b})$: one number "
                         r"standing for the whole profile", fontsize=10, ha="center")
    ax.text(0.62, -0.56, rf"${b}$ is the bulk, weighted by the velocity: between the wall "
                         r"and the centreline values", fontsize=9, ha="center", color=TCOL)
    ax.set_xlim(-0.32, 2.30); ax.set_ylim(-0.64, 1.22); ax.axis("off")
    ax.set_title(rf"What ${h}$ summarises", fontsize=12, fontweight="bold")


def _subchannel(ax, kind, p=1.0, d=1/1.33):
    """One unit cell of a rod lattice: the flow area shaded, the wetted perimeter bold."""
    if kind == "square":
        cell = np.array([[0, 0], [p, 0], [p, p], [0, p]], float)
        centres = cell.copy(); frac = 0.25; title = "square lattice"
        De_over_d = 4/np.pi*(p/d)**2 - 1          # De/d, NOT De: the label says "d"
    else:
        h = p*np.sqrt(3)/2
        cell = np.array([[0, 0], [p, 0], [p/2, h]], float)
        centres = cell.copy(); frac = 1/6.0; title = "triangular lattice"
        De_over_d = 2*np.sqrt(3)/np.pi*(p/d)**2 - 1
    ax.add_patch(Polygon(cell, closed=True, fc="#eaf2fb", ec="0.45", lw=1.2, ls="--"))
    for c in centres:
        ax.add_patch(Circle(c, d/2, fc=WALL, ec="k", lw=1.6, zorder=3))
    ax.set_title(f"{title}:  $D_e = 4A/P = {De_over_d:.2f}\\,d$   at $p/d$ = {p/d:.2f}",
                 fontsize=10)
    ax.text(p/2, -0.66, f"{len(centres)} rods share this cell, each contributing "
                        f"{frac:.2f} of its circumference to $P$", fontsize=8.5,
            ha="center", color="0.3")
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-d/2 - 0.08, p + d/2 + 0.08)
    ax.set_ylim(-0.78, (p if kind == "square" else p*np.sqrt(3)/2) + d/2 + 0.08)


def equivalent_diameter(fig, axes):
    _subchannel(axes[0], "square"); _subchannel(axes[1], "triangular")
    fig.suptitle("The channel a reactor actually has. $A$ is the shaded area left between "
                 "the rods, $P$ the rod surface bounding it.", fontsize=11, y=1.03)


def main():
    for sym, png, pdf in ((SYM_NB, True, False), (SYM_NOTES, False, True)):
        fig, ax = plt.subplots(figsize=(9.0, 4.8))
        boundary_layer(ax, sym); plt.tight_layout(); save(fig, "04_boundary_layer", png, pdf)

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.2))
    equivalent_diameter(fig, axes); plt.tight_layout(); save(fig, "04_equivalent_diameter")


if __name__ == "__main__":
    main()
