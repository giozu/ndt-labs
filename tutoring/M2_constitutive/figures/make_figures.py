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


def fracture_analysis_diagram():
    """Stress-temperature diagram for crack initiation and arrest, after Weisman (1977),
    Fig. 10.9 and section 10.4, with his letters and his NDT.

    NDT is where yield (B) and tensile strength (A) coincide, the flaw-free NDT. With a
    small flaw the fracture stress C drops to the yield curve about 50 degF (28 K) higher,
    the NDT with a small flaw. The crack-arrest curve D sits on the lower fracture
    propagation stress, about 6500 psi (45 MPa), meets B at FTE ~ NDT + 60 degF (33 K) and
    A at FTP soon after. Temperature is measured from NDT; differences in degF convert with
    5/9 alone. Schematic, as Weisman's is: no stress values but the lower one.
    """
    T = np.linspace(-25, 75, 700)                     # T - NDT, degC
    T_f, FTE, FTP = 27.8, 33.3, 36.0                  # NDT small flaw (+50 degF), +60 degF; FTP just after, as Weisman draws it
    A = 1.40 - 0.004*T                                # tensile strength
    B = np.minimum(1.00 + 0.40*np.exp(-T/9.0), A)     # yield, meets A at NDT (T = 0)
    B = np.where(T < 0, A, B)                         # below NDT the two coincide
    def at(curve, t):
        return np.interp(t, T, curve)
    # C, fracture stress with a small flaw: on B up to T_f, then up to A at FTP
    s = np.clip((T - T_f)/(FTP - T_f), 0, 1)
    C = B + (A - B)*(3*s**2 - 2*s**3)
    # D, crack arrest: flat on the lower stress, then convex up through B at FTE to A at FTP
    shelf, T0 = 0.13, 8.0
    yE, yP = at(B, FTE), at(A, FTP)
    pw = np.log((yE - shelf)/(yP - shelf))/np.log((FTE - T0)/(FTP - T0))
    D = shelf + (yP - shelf)*(np.clip(T - T0, 0, None)/(FTP - T0))**pw
    D = np.where(T > FTP, np.nan, D)
    assert pw > 1, "D is convex, as in Weisman's figure"

    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.plot(T, A, color="0.2", lw=1.8)
    ax.plot(T, B, color="0.2", lw=1.8)
    ax.plot(T, C, color="tab:blue", lw=1.8, ls="--")
    ax.plot(T, D, color="tab:red", lw=3, ls=(0, (6, 3)))
    ax.text(50, at(A, 50) + 0.04, r"A, $S_{UTS}$  tensile strength", fontsize=10)
    ax.text(50, at(B, 50) - 0.09, r"B, $S_y$  yield strength", fontsize=10)
    ax.text(8, 1.47, "C  tensile strength\n    with a small flaw", color="tab:blue",
            fontsize=10)
    ax.text(34, 0.55, "D  crack arrest\n    curve", color="tab:red", fontsize=10)
    ax.axhline(shelf, xmax=(T0 + 25)/100, color="tab:red", lw=3, ls=(0, (6, 3)))
    ax.text(-24, shelf - 0.07, "lower fracture propagation stress, about 45 MPa (6500 psi)",
            fontsize=9, color="tab:red")
    ax.fill_between(T, shelf, D, where=(T > T0) & (T < FTP), color="tab:red", alpha=0.08)
    ax.plot([FTE, FTP], [yE, yP], "o", color="k", ms=5)
    ax.text(FTP + 1, yP + 0.03, "FTP", fontsize=10)
    marks = [(0, "NDT\n-12 °C (10 °F)"), (T_f, "NDT with a\nsmall flaw\n16 °C (60 °F)"),
             (FTE, "FTE\n21 °C\n(70 °F)")]
    for t, lab, ha, dx in zip(*zip(*marks), ("left", "right", "left"), (1, -1, 1)):
        ax.axvline(t, color="0.5", ls=":", lw=1)
        ax.text(t + dx, 1.86, lab, fontsize=9, va="top", ha=ha)
    ax.text(5, 0.55, "a running crack\npropagates", color="tab:red", fontsize=10,
            ha="center")
    ax.text(58, 0.55, "a running crack\nis arrested", color="tab:red", fontsize=10,
            ha="center")
    ax.annotate("", xy=(30, 1.98), xytext=(0, 1.98), annotation_clip=False,
                arrowprops=dict(arrowstyle="->", color="tab:purple", lw=2))
    ax.text(32, 1.98, "irradiation moves NDT, and the whole diagram with it, to the right",
            color="tab:purple", fontsize=10, va="center")
    ax.set_xlim(-25, 75); ax.set_ylim(0, 1.9)
    ax.set_yticks([])
    # Absolute axis with Weisman's carbon steel: NDT = 10 degF. Curves are computed in
    # T - NDT; only the labels are absolute.
    from matplotlib.ticker import FixedLocator, FixedFormatter
    T_NDT = (10 - 32)*5/9
    tc = np.arange(-30, 70, 10)
    ax.xaxis.set_major_locator(FixedLocator(tc - T_NDT))
    ax.xaxis.set_major_formatter(FixedFormatter([f"{t:g}".replace("-", "\u2212") for t in tc]))
    ax.set_xlabel("temperature (°C), carbon steel with NDT = -12 °C (10 °F), "
                  "Weisman's example")
    sec = ax.secondary_xaxis(-0.16, functions=(lambda x: (x + T_NDT)*9/5 + 32,
                                              lambda f: (f - 32)*5/9 - T_NDT))
    sec.set_xticks(np.arange(-20, 180, 20))
    sec.set_xlabel("(°F)")
    ax.set_ylabel("stress, applied plus residual  →")
    ax.grid(alpha=0.25)
    plt.tight_layout()
    save(fig, "03_fracture_analysis_diagram")


def main():
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 3.3))
    for ax in axes:
        ax.set_aspect("equal"); ax.axis("off")
    plane_stress(axes[0]); plane_strain(axes[1]); generalised_plane_strain(axes[2])
    fig.suptitle("Three reductions of the 3-D law. Red is what you impose, blue is what "
                 "follows - and note where $z$ points in each.", fontsize=12, y=0.97)
    plt.tight_layout()
    save(fig, "03_plane_hypotheses")
    fracture_analysis_diagram()


if __name__ == "__main__":
    main()
