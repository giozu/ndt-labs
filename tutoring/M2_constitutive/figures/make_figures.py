"""The drawings of module M2.

They live here, beside the notebook, rather than inside it: the plotting code is long,
teaches nothing and made the notebook unreadable on the repository page. The notebook
shows the resulting images; this script is the only owner of them.

    python3 make_figures.py

writes the PNGs the notebook embeds into this folder. If NDT_COURSE_NOTES_FIGURES points
at a directory it also writes the PDF versions there, so the notebook and the course notes
cannot drift apart.

The file names carry the prefix of the course-notes CHAPTER that owns the figure, not of
the module: M2 feeds chapter 3, so the prefix is `03_`. Chapters 3 to 6 carried prefixes
from an older chapter order until 2026-09-23, when all eight were renamed together.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch, Ellipse

HERE = os.path.dirname(os.path.abspath(__file__))
NOTES = os.environ.get("NDT_COURSE_NOTES_FIGURES", "")

IMPOSED, RESULT, BODY, EDGE = "tab:red", "tab:blue", "0.90", "0.35"


def save(fig, name):
    fig.savefig(os.path.join(HERE, name + ".png"), dpi=110, bbox_inches="tight")
    if os.path.isdir(NOTES):
        fig.savefig(os.path.join(NOTES, name + ".pdf"), bbox_inches="tight")
    plt.close(fig)


def _arrow(ax, p, q, colour, lw=1.6, ms=9):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms,
                                 color=colour, lw=lw, shrinkA=0, shrinkB=0,
                                 zorder=4))


def _triad(ax, o, names, dirs, L=0.32, shrink=(1.0, 0.60, 1.0)):
    """Axes drawn where the body is. `dirs` are the three unit directions in the drawing,
    `names` their labels; the out-of-plane one of the hypothesis is always among them and
    is always drawn bold, because getting it wrong is the mistake this figure exists to
    prevent."""
    for (dx, dy), nm, bold, k in zip(dirs, names, (False, False, True), shrink):
        _arrow(ax, o, (o[0] + k*L*dx, o[1] + k*L*dy), "k", lw=1.2, ms=8)
        ax.text(o[0] + (k*L + 0.075)*dx, o[1] + (k*L + 0.075)*dy, nm, fontsize=10,
                ha="center", va="center",
                fontweight="bold" if bold else "normal")


IN, UP, DEPTH = (1.0, 0.0), (0.0, 1.0), (0.46, 0.40)


def _box(ax, o, w, h, dep=DEPTH, d=0.55, top=BODY, side="0.82", face="0.96"):
    """An axonometric box: o is the near-bottom-left corner, w x h the near face."""
    sx, sy = d*dep[0], d*dep[1]
    near = [(o[0], o[1]), (o[0] + w, o[1]), (o[0] + w, o[1] + h), (o[0], o[1] + h)]
    lid = [(o[0], o[1] + h), (o[0] + w, o[1] + h),
           (o[0] + w + sx, o[1] + h + sy), (o[0] + sx, o[1] + h + sy)]
    rgt = [(o[0] + w, o[1]), (o[0] + w + sx, o[1] + sy),
           (o[0] + w + sx, o[1] + h + sy), (o[0] + w, o[1] + h)]
    for poly, fc in ((lid, top), (rgt, side), (near, face)):
        ax.add_patch(Polygon(poly, closed=True, fc=fc, ec=EDGE, lw=1.1, zorder=2))


def _verdict(ax, x, imposed, follows):
    ax.text(x, 0.72, "imposed\n" + imposed, fontsize=10.5, color=IMPOSED, ha="center",
            va="center", fontweight="bold")
    ax.text(x, 0.18, "follows\n" + follows, fontsize=9.5, color=RESULT, ha="center",
            va="center")


def plane_stress(ax):
    """Thin plate, z through the thickness: the free faces ARE the hypothesis."""
    ax.set_title("plane stress", fontsize=12, fontweight="bold", pad=10)
    _box(ax, (0.35, 0.42), 1.55, 0.13)
    for y in (0.45, 0.52):                                  # loaded in its own plane
        _arrow(ax, (-0.05, y), (0.31, y), RESULT, lw=1.3, ms=8)
        _arrow(ax, (1.94, y), (2.30, y), RESULT, lw=1.3, ms=8)
    # a leader line, NOT an arrow into the face: nothing acts there, that is the point
    ax.plot([1.13, 1.13], [0.62, 0.95], color=IMPOSED, lw=0.9, ls=":")
    ax.text(1.13, 1.00, "faces free:\nnothing acts on them", fontsize=9, color=IMPOSED,
            ha="center")
    ax.text(1.13, 0.08, "thin plate, loaded in its own plane", fontsize=9.5,
            ha="center", style="italic")
    _triad(ax, (0.02, 0.95), ("x", "y", "z"), [IN, DEPTH, UP])
    _verdict(ax, 2.90, r"$\sigma_{zz}=0$", r"$\varepsilon_{zz}\neq 0$, it thins")
    ax.set_xlim(-0.25, 3.45); ax.set_ylim(0.0, 1.32)


def plane_strain(ax):
    """Long body, z ALONG it, ends held. The wall must pull to stop Poisson contraction."""
    ax.set_title("plane strain", fontsize=12, fontweight="bold", pad=10)
    _box(ax, (0.62, 0.30), 1.30, 0.52)
    for x, sgn in ((0.62, -1), (1.92, +1)):                 # the two rigid ends
        ax.add_patch(Polygon([(x + sgn*0.11, 0.22), (x, 0.22), (x, 0.96),
                              (x + sgn*0.11, 0.96)], closed=True, fc="0.55", ec="k",
                             lw=1.0, hatch="///", zorder=5))
    for y in (0.40, 0.56, 0.72):                            # pulled OUT: see the note
        _arrow(ax, (0.56, y), (0.24, y), RESULT, lw=1.3, ms=8)
        _arrow(ax, (1.98, y), (2.30, y), RESULT, lw=1.3, ms=8)
    ax.text(1.27, 1.13, r"in-plane tension makes it want to contract along $z$;"
                        "\nthe ends pull back to stop it", fontsize=8.5, ha="center",
            color="0.25")
    ax.text(1.27, 0.08, "long body, ends held", fontsize=9.5, ha="center",
            style="italic")
    _triad(ax, (0.06, 0.40), ("x", "y", "z"), [UP, DEPTH, IN])
    _verdict(ax, 2.90, r"$\varepsilon_{zz}=0$",
             r"$\sigma_{zz}=\nu(\sigma_{xx}+\sigma_{yy})$")
    ax.set_xlim(-0.25, 3.45); ax.set_ylim(0.0, 1.32)


def generalised_plane_strain(ax):
    """Long cylinder, z ALONG the axis, ends free: the resultant is prescribed, not zero."""
    ax.set_title("generalised plane strain", fontsize=12, fontweight="bold", pad=10)
    x0, x1, yc, ro, ri, ex = 0.62, 1.92, 0.56, 0.30, 0.18, 0.15
    ax.add_patch(Polygon([(x0, yc - ro), (x1, yc - ro), (x1, yc + ro), (x0, yc + ro)],
                         closed=True, fc=BODY, ec=EDGE, lw=1.1, zorder=2))
    for x, fc in ((x0, "0.97"), (x1, "0.86")):
        ax.add_patch(Ellipse((x, yc), 2*ex, 2*ro, fc=fc, ec=EDGE, lw=1.1, zorder=3))
        ax.add_patch(Ellipse((x, yc), 2*ex*ri/ro, 2*ri, fc="w", ec=EDGE, lw=1.0, zorder=4))
    # sigma_zz over the annulus, on BOTH ends (or the body is not in equilibrium) and of
    # BOTH signs: the outer row pulls, the inner row pushes. Only the resultant N is
    # imposed, so the field is free to change sign over the section; with N = 0 it must.
    for x_end, out in ((x0 - ex, -1), (x1 + ex, +1)):
        for s in (+1, -1):
            for f, tension in ((0.88, True), (0.62, False)):
                y = yc + s*f*ro
                near, far = x_end + out*0.03, x_end + out*0.28
                _arrow(ax, *(((near, y), (far, y)) if tension else ((far, y), (near, y))),
                       RESULT, lw=1.3, ms=7)
    ax.text(1.27, 1.03, r"$N=0$ for a temperature gradient alone;" + "\n"
                        r"$N=p\,\pi r_i^2$ for pressure on closed heads",
            fontsize=8.5, ha="center", color="0.25")
    ax.text(1.27, 0.08, "long cylinder, ends free", fontsize=9.5, ha="center",
            style="italic")
    _triad(ax, (-0.20, 0.10), ("r", r"$\theta$", "z"), [UP, DEPTH, IN])
    _verdict(ax, 2.90, r"$\varepsilon_{zz}=$ const," + "\nvalue unknown",
             r"$\int_A\sigma_{zz}\,dA=N$" + "\nfixes it")
    ax.set_xlim(-0.25, 3.45); ax.set_ylim(0.0, 1.32)


def main():
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 3.3))
    for ax in axes:
        ax.set_aspect("equal"); ax.axis("off")
    plane_stress(axes[0]); plane_strain(axes[1]); generalised_plane_strain(axes[2])
    fig.suptitle("Three reductions of the 3-D law. Red is what you impose, blue is what "
                 "follows - and note where $z$ points in each.", fontsize=12, y=0.97)
    plt.tight_layout()
    save(fig, "03_plane_hypotheses")


if __name__ == "__main__":
    main()
