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


def _fad_curves():
    """The four curves of the generalised FAD, shared by the diagram and its regimes."""
    T = np.linspace(-45, 90, 900)                     # T - NDT, degC
    H, FTE, FTP, T_nf = 16.7, 33.3, 66.7, -28.0       # +30, +60, +120 degF; S_y = S_u flaw-free
    A = 1.40 - 0.002*T                                # tensile strength
    tau = -T_nf/np.log((1.40 - 0.002*T_nf - 0.95)/0.05)
    B = np.minimum(0.95 + 0.05*np.exp(-T/tau), A)     # yield; meets A at T_nf
    at = lambda curve, t: np.interp(t, T, curve)
    # C, fracture initiation from a small flaw: on B up to NDT (point A of the DWT), then up
    # to A, at FTP
    s = np.clip(T/FTP, 0, 1)
    C = B + (A - B)*(3*s**2 - 2*s**3)
    # D, crack arrest: shelf, convex up through 1/2 S_y and S_y, then bending onto A at FTP
    shelf = 0.15                                      # 34-55 MPa (5-8 ksi) for a ~300 MPa steel
    yE, yP = at(B, FTE), at(A, FTP)
    pw = np.log((0.5 - shelf)/(yE - shelf))/np.log(H/FTE)
    D = shelf + (yE - shelf)*(np.clip(T, 0, FTE)/FTE)**pw
    m0, h = (yE - shelf)*pw/FTE, FTP - FTE
    q = m0*h/(yP - yE)
    D = np.where(T > FTE, yP - (yP - yE)*(1 - np.clip((T - FTE)/h, 0, 1))**q, D)
    D = np.where(T > FTP, A, D)
    assert np.all(np.diff(D[(T > 0) & (T < FTP)]) > 0), "D rises from NDT to FTP"

    return T, A, B, C, D, shelf, (H, FTE, FTP, T_nf), at


def fracture_analysis_diagram():
    """The generalised Fracture Analysis Diagram, after Jawad and Farr (2019), Figs. 4.12
    and 4.14, with Weisman's letters for the curves (1977, Fig. 10.9).

    NDT is the drop-weight NDT (ASTM E208): a notched brittle weld bead, loaded to no more
    than yield, stops breaking. Point A, small flaw at yield. The crack-arrest curve D
    passes through 1/2 S_y at NDT + 30 degF, S_y at FTE = NDT + 60 degF and S_u at
    FTP = NDT + 120 degF; the steps are differences, so they convert with 5/9 alone.
    Stress in units of S_y at NDT. Schematic: the shapes and the marked steps are the content.
    """
    T, A, B, C, D, shelf, (H, FTE, FTP, T_nf), at = _fad_curves()
    yE, yP = at(B, FTE), at(A, FTP)
    fig, ax = plt.subplots(figsize=(10.5, 6))
    ax.plot(T, A, color="0.2", lw=1.8)
    ax.plot(T, B, color="0.2", lw=1.8)
    ax.plot(T, C, color="tab:blue", lw=1.8, ls="--")
    ax.plot(T, D, color="tab:red", lw=3)
    ax.text(70, at(A, 70) + 0.04, r"A, $S_{UTS}$  tensile strength", fontsize=10)
    ax.text(70, at(B, 70) - 0.09, r"B, $S_y$  yield strength", fontsize=10)
    ax.text(30, 1.30, "C  tensile strength\n    with a small flaw", color="tab:blue", fontsize=10, va="top",
            ha="right")
    ax.text(40, 0.62, "D  crack arrest\n    (CAT curve)", color="tab:red", fontsize=10)
    ax.plot(0, at(B, 0), "o", color="tab:blue", ms=7, zorder=6)
    ax.annotate("drop-weight test: small\nflaw (about 25 mm, 1 in) at yield", xy=(0, at(B, 0)),
                xytext=(-28, 1.12), fontsize=9, color="tab:blue",
                arrowprops=dict(arrowstyle="->", color="tab:blue", lw=1))
    ax.plot(T_nf, at(A, T_nf), "o", color="0.2", ms=5)
    ax.text(T_nf - 1, at(A, T_nf) + 0.05, "$S_y = S_u$, no flaw", fontsize=9, ha="center")
    # larger flaws: lower initiation stresses, joining D (Jawad and Farr, Fig. 4.14)
    for lev, lab in ((0.75, "100-200 mm (4-8 in)"), (0.5, "200-300 mm (8-12 in)"),
                     (0.25, "0.3-0.6 m (1-2 ft)")):
        Tj = T[np.argmax(D >= lev)]
        ax.plot([-45, Tj], [lev, lev], color="tab:blue", lw=1.1, ls=":")
        ax.text(-44, lev + 0.02, "flaw " + lab, color="tab:blue", fontsize=8.5)
    ax.axhspan(0, shelf, color="tab:green", alpha=0.10)
    ax.text(-44, 0.05, "below 34-55 MPa (5-8 ksi): no crack propagates, at any temperature",
            fontsize=9, color="tab:green")
    ax.fill_between(T, shelf, D, where=(T > 0) & (T < FTP), color="tab:red", alpha=0.07)
    ax.text(-14, 0.86, "a running crack\npropagates", color="tab:red", fontsize=10,
            ha="center")
    ax.text(58, 0.40, "a running crack\nis arrested", color="tab:red", fontsize=10,
            ha="center")
    ax.annotate("", xy=(30, 1.83), xytext=(0, 1.83), annotation_clip=False,
                arrowprops=dict(arrowstyle="->", color="tab:purple", lw=2))
    ax.text(32, 1.83, "irradiation moves NDT, and the whole diagram with it, to the right",
            color="tab:purple", fontsize=10, va="center")
    ticks = [(0, "NDT"), (H, "NDT + 17 °C\n(30 °F)"), (FTE, "FTE\nNDT + 33 °C\n(60 °F)"),
             (FTP, "FTP\nNDT + 67 °C\n(120 °F)")]
    for t, _ in ticks:
        ax.axvline(t, color="0.5", ls=":", lw=1)
    ax.set_xticks([t for t, _ in ticks]); ax.set_xticklabels([l for _, l in ticks])
    ax.set_xlim(-45, 90); ax.set_ylim(0, 1.75)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels([r"$\frac{1}{4}S_y$", r"$\frac{1}{2}S_y$", r"$\frac{3}{4}S_y$", r"$S_y$"])
    ax.set_xlabel("temperature  →")
    ax.set_ylabel("nominal tensile stress\n(units of $S_y$ at NDT)")
    ax.grid(alpha=0.25)
    plt.tight_layout()
    save(fig, "03_fracture_analysis_diagram")


def charpy_transition():
    """Charpy energy against temperature for a ferritic steel, after Murty and Charit
    (2013), Fig. 5.20: the two shelves, the two transitions they draw, and the 40 J
    convention for the DBTT of their section 5.1.4.1. Schematic: no temperature values.
    """
    T = np.linspace(-1, 1, 400)
    low, up = 0.06, 1.0
    E = low + (up - low)*0.5*(1 + np.tanh(3.2*T))
    def T_at(e):
        return np.interp(e, E, T)
    e15, e40 = 0.13, 0.27                          # 20 J (15 ft lb) and 40 J, schematic
    t_duct, t_dbtt, t_frac = T_at(e15), T_at(e40), 0.55
    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.plot(T, E, color="k", lw=2.5)
    for t, lab in ((t_duct, "ductility\ntransition"), (t_frac, "fracture\ntransition")):
        ax.axvline(t, color="0.4", lw=1.2)
        ax.text(t, 1.12, lab, ha="center", va="bottom", fontsize=10)
    ax.plot([-1, t_dbtt], [e40, e40], color="tab:red", ls="--", lw=1.2)
    ax.plot([t_dbtt, t_dbtt], [0, e40], color="tab:red", ls="--", lw=1.2)
    ax.text(-0.98, e40 + 0.02, "40 J (30 ft·lb)", color="tab:red", fontsize=9)
    ax.text(t_dbtt + 0.02, 0.01, "DBTT", color="tab:red", fontsize=10, fontweight="bold")
    ax.text(-0.98, e15 + 0.015, "about 20 J (15 ft·lb)", color="0.3", fontsize=9)
    ax.plot([-1, t_duct], [e15, e15], color="0.4", ls=":", lw=1)
    # the five arrows of Murty and Charit's Fig. 5.20: two leftwards and one rightwards
    # from the ductility transition, two rightwards from the fracture transition
    arrows = [(t_duct, -0.97, 0.78, "brittle failure\nin service"),
              (t_duct, -0.97, 0.40, "easy crack\ninitiation"),
              (t_duct, 0.97, 0.62, "ductile behaviour in service"),
              (t_frac, 0.97, 1.02, "shear fracture"),
              (t_frac, 0.97, 0.30, "difficult crack initiation\nand propagation")]
    for x0, x1, y, lab in arrows:
        ax.annotate("", xy=(x1, y), xytext=(x0, y),
                    arrowprops=dict(arrowstyle="->", lw=1.3))
        right = x1 > x0
        ax.text(x1 - 0.02 if right else x1 + 0.02, y + 0.03, lab, fontsize=9.5,
                ha="right" if right else "left", va="bottom")
    ax.text(-0.97, low + 0.02, "lower shelf: cleavage", fontsize=9, color="0.35")
    ax.text(0.97, up - 0.07, "upper shelf: ductile tearing", fontsize=9, color="0.35",
            ha="right")
    ax.set_xlim(-1, 1); ax.set_ylim(0, 1.25)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel("temperature  →"); ax.set_ylabel("Charpy absorbed energy  →")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    plt.tight_layout()
    save(fig, "03_charpy_transition")


def fad_regimes():
    """The same diagram, shaded by what happens to a crack (small flaw), four regimes:
    I below the lower propagation stress, II above D but below the initiation curve C,
    III above both, IV below D (right of the crack-arrest curve). Larger flaws lower the
    initiation line (dotted), and so turn part of II into III.
    """
    T, A, B, C, D, shelf, (H, FTE, FTP, T_nf), at = _fad_curves()
    top = np.maximum(A, B)
    fig, ax = plt.subplots(figsize=(10.5, 6))
    col = {"I": "#2ca02c", "II": "#ffbf00", "III": "#d62728", "IV": "#1f77b4"}
    ax.fill_between(T, 0, shelf, color=col["I"], alpha=0.30, lw=0)
    up = np.maximum(D, shelf)
    ax.fill_between(T, shelf, np.minimum(up, top), color=col["IV"], alpha=0.25, lw=0)
    ax.fill_between(T, up, np.maximum(np.minimum(C, top), up), where=C > up,
                    color=col["II"], alpha=0.35, lw=0)
    ax.fill_between(T, np.maximum(C, up), top, where=top > np.maximum(C, up),
                    color=col["III"], alpha=0.30, lw=0)
    ax.plot(T, A, color="0.2", lw=1.6); ax.plot(T, B, color="0.2", lw=1.6)
    ax.plot(T, C, color="tab:blue", lw=1.6, ls="--"); ax.plot(T, D, color="tab:red", lw=2.6)
    for lev in (0.75, 0.5, 0.25):
        Tj = T[np.argmax(D >= lev)]
        ax.plot([-45, Tj], [lev, lev], color="0.35", lw=1, ls=":")
    ax.text(-44, 0.765, "dotted: larger flaws start lower, and turn II into III", fontsize=8.5,
            color="0.3")
    lab = [("I", -20, 0.05, "I  no crack can run, at any temperature"),
           ("II", -20, 0.52, "II  nothing starts from a small flaw,\n     but a crack that starts runs"),
           ("III", -14, 1.22, "III  a crack starts and runs:\n      brittle fracture"),
           ("IV", 55, 0.55, "IV  a crack that starts\n      is arrested")]
    for k, x, y, t in lab:
        ax.text(x, y, t, fontsize=10, fontweight="bold", color=col[k] if k != "II" else "#b07d00")
    ticks = [(0, "NDT"), (H, "NDT + 17 °C\n(30 °F)"), (FTE, "FTE\nNDT + 33 °C\n(60 °F)"),
             (FTP, "FTP\nNDT + 67 °C\n(120 °F)")]
    for t, _ in ticks:
        ax.axvline(t, color="0.5", ls=":", lw=1)
    ax.set_xticks([t for t, _ in ticks]); ax.set_xticklabels([l for _, l in ticks])
    ax.set_xlim(-45, 90); ax.set_ylim(0, 1.6)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels([r"$\frac{1}{4}S_y$", r"$\frac{1}{2}S_y$", r"$\frac{3}{4}S_y$", r"$S_y$"])
    ax.set_xlabel("temperature  →")
    ax.set_ylabel("nominal tensile stress\n(units of $S_y$ at NDT)")
    plt.tight_layout()
    save(fig, "03_fad_regimes")


def fad_criteria():
    """The four design criteria as rectangles (minimum temperature, maximum stress), each
    with its upper-left corner on the crack-arrest curve D. Criterion 1 is the band below
    34.5 MPa at any temperature; 2, 3, 4 start at NDT + 17, FTE and FTP and reach 1/2 S_y,
    S_y and S_u. On the regimes of fad_regimes, faintly, for context.
    """
    from matplotlib.patches import Rectangle
    T, A, B, C, D, shelf, (H, FTE, FTP, T_nf), at = _fad_curves()
    top = np.maximum(A, B)
    fig, ax = plt.subplots(figsize=(10.5, 6))
    up = np.maximum(D, shelf)
    ax.fill_between(T, 0, shelf, color="#2ca02c", alpha=0.12, lw=0)
    ax.fill_between(T, shelf, np.minimum(up, top), color="#1f77b4", alpha=0.10, lw=0)
    ax.fill_between(T, up, top, where=top > up, color="#d62728", alpha=0.08, lw=0)
    ax.plot(T, A, color="0.3", lw=1.4); ax.plot(T, B, color="0.3", lw=1.4)
    ax.plot(T, D, color="tab:red", lw=2.8)
    x1 = 90
    s1 = 0.115                                       # 34.5 MPa, low end of the shelf band
    boxes = [(-45, s1, "1", "any T,  σ ≤ 34.5 MPa (5 ksi)", "#2ca02c"),
             (H, 0.5, "2", "T ≥ NDT + 17 °C,  σ ≤ ½ S$_y$", "#9467bd"),
             (FTE, at(B, FTE), "3", "T ≥ FTE,  σ ≤ S$_y$", "#1f77b4"),
             (FTP, at(A, FTP), "4", "T ≥ FTP,  any σ", "#ff7f0e")]
    for k, (t0, smax, n, lab, c) in enumerate(boxes):
        ax.add_patch(Rectangle((t0, 0), x1 - t0, smax, fill=False, ec=c, lw=2.2,
                               ls=(0, (5, 2)), zorder=4 + k))
        if n != "1":
            ax.plot(t0, smax, "o", color=c, ms=8, zorder=10)
        ax.text(t0 + 1.5 if n != "1" else -43, smax + 0.03 if n != "1" else 0.035,
                f"{n}   {lab}", color=c, fontsize=10, fontweight="bold", zorder=10)
    ax.text(-30, 0.62, "covered by no criterion:\nhere a crack can run", color="#a33",
            fontsize=10, style="italic")
    ax.text(5, 1.25, "D, crack-arrest curve: the corner\nof every rectangle sits on it",
            color="tab:red", fontsize=10)
    ticks = [(0, "NDT"), (H, "NDT + 17 °C\n(30 °F)"), (FTE, "FTE\nNDT + 33 °C\n(60 °F)"),
             (FTP, "FTP\nNDT + 67 °C\n(120 °F)")]
    for t, _ in ticks:
        ax.axvline(t, color="0.6", ls=":", lw=1)
    ax.set_xticks([t for t, _ in ticks]); ax.set_xticklabels([l for _, l in ticks])
    ax.set_xlim(-45, 90); ax.set_ylim(0, 1.6)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels([r"$\frac{1}{4}S_y$", r"$\frac{1}{2}S_y$", r"$\frac{3}{4}S_y$", r"$S_y$"])
    ax.set_xlabel("temperature  →")
    ax.set_ylabel("nominal tensile stress\n(units of $S_y$ at NDT)")
    plt.tight_layout()
    save(fig, "03_fad_criteria")


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
    fad_regimes()
    fad_criteria()
    charpy_transition()


if __name__ == "__main__":
    main()
