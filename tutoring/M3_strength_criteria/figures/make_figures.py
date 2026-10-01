"""The drawings of module M3.

They live here, beside the notebook, rather than inside it: the plotting code is long,
teaches nothing and made the notebook unreadable on the repository page. The notebook
shows the resulting images; this script is the only owner of them.

    python3 make_figures.py

writes the PNGs the notebook embeds into this folder. If NDT_COURSE_NOTES_FIGURES points
at a directory it also writes the PDF versions there.

File names carry the prefix of the course-notes CHAPTER that owns the figure, not of the
module: M3 feeds chapter 8, so the prefix is `08_`.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
NOTES = os.environ.get("NDT_COURSE_NOTES_FIGURES", "")
VM, TR, HYD = "tab:blue", "tab:green", "0.35"


def save(fig, name):
    fig.savefig(os.path.join(HERE, name + ".png"), dpi=110, bbox_inches="tight")
    if os.path.isdir(NOTES):
        fig.savefig(os.path.join(NOTES, name + ".pdf"), bbox_inches="tight")
    plt.close(fig)


# The deviatoric plane: an orthonormal pair perpendicular to the hydrostatic direction.
N = np.ones(3)/np.sqrt(3)
U = np.array([1.0, -1.0, 0.0])/np.sqrt(2)
V = np.cross(N, U)


def _loci(sY, m=721):
    """The two yield loci in the deviatoric plane, computed the way the notebook does:
    sample a direction, evaluate the criterion on it, scale until it equals sY. Nothing
    here assumes the hexagon's orientation - it comes out of the Tresca function."""
    t = np.linspace(0, 2*np.pi, m)
    d = np.cos(t)[:, None]*U + np.sin(t)[:, None]*V          # traceless by construction
    assert np.abs(d.sum(axis=1)).max() < 1e-12, "the sampling left the deviatoric plane"
    tr = d.max(axis=1) - d.min(axis=1)                        # Tresca of a deviator
    vm = np.sqrt(1.5*np.sum(d*d, axis=1))                     # von Mises of a deviator
    return d*(sY/tr)[:, None], d*(sY/vm)[:, None]


def surfaces(ax, sY=250.0, L=330.0):
    """The two yield surfaces in principal-stress space: prisms along the hydrostatic
    axis. That they are PRISMS, open at both ends, is the whole point: add any amount of
    hydrostatic stress and you never leave them."""
    hexa, circ = _loci(sY)
    for s in (-1, 1):                                         # the two open ends
        for locus, col, lw in ((circ, VM, 1.6), (hexa, TR, 1.8)):
            p = locus + s*L*N
            ax.plot(p[:, 0], p[:, 1], p[:, 2], color=col, lw=lw)
    for k in range(0, 720, 120):                              # the six Tresca edges
        a, b = hexa[k] - L*N, hexa[k] + L*N
        ax.plot(*zip(a, b), color=TR, lw=1.2)
    for k in range(0, 720, 90):                               # a few cylinder rulings
        a, b = circ[k] - L*N, circ[k] + L*N
        ax.plot(*zip(a, b), color=VM, lw=0.7, alpha=0.55)
    ax.plot(*zip(-1.20*L*N, 1.20*L*N), color=HYD, lw=1.6, ls="--")
    ax.text(*(1.24*L*N), r"$\sigma_1=\sigma_2=\sigma_3$", color=HYD, fontsize=9)
    for e, nm in zip(np.eye(3), (r"$\sigma_1$", r"$\sigma_2$", r"$\sigma_3$")):
        ax.plot(*zip(np.zeros(3), 0.72*L*e), color="k", lw=1.0)
        ax.text(*(0.80*L*e), nm, fontsize=11)
    ax.set_title("Both surfaces are prisms along the hydrostatic axis", fontsize=11,
                 fontweight="bold", pad=0)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=20, azim=34); ax.set_axis_off()
    lim = 0.80*L
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)


def deviatoric_plane(ax, sY=250.0):
    """The same two surfaces seen down the hydrostatic axis: a hexagon inscribed in a
    circle, touching at six points."""
    hexa, circ = _loci(sY)
    h2 = np.c_[hexa @ U, hexa @ V]
    c2 = np.c_[circ @ U, circ @ V]
    ax.plot(c2[:, 0], c2[:, 1], color=VM, lw=2.0, label="von Mises")
    ax.plot(h2[:, 0], h2[:, 1], color=TR, lw=2.0, label="Tresca")
    # The six points where the hexagon meets the circle are found, not guessed: t = 0 is
    # the pure-shear direction, which is where Tresca sits FURTHEST inside, so stepping by
    # 60 degrees from there lands on the edge midpoints instead of the vertices.
    k0 = int(np.argmin(np.linalg.norm(hexa - circ, axis=1)))
    touch = [(k0 + 120*i) % 720 for i in range(6)]
    assert np.allclose(np.linalg.norm(hexa[touch] - circ[touch], axis=1), 0, atol=1e-9), \
        "those are not the touching points"
    for k in touch:
        ax.plot(*h2[k], "o", color=TR, ms=5, zorder=5)
    for e, nm in zip(np.eye(3), (r"$\sigma_1$", r"$\sigma_2$", r"$\sigma_3$")):
        p = np.array([e @ U, e @ V])*1.30*sY
        ax.plot([0, p[0]], [0, p[1]], color="k", lw=0.9, ls=":")
        ax.text(p[0]*1.10, p[1]*1.10, nm, fontsize=10, ha="center", va="center")
    ax.plot(0, 0, "o", color=HYD, ms=6)
    ax.text(0.04*sY, -0.16*sY, "hydrostatic axis,\nseen end on", fontsize=8.5, color=HYD)
    ax.set_title("Looking down that axis", fontsize=11, fontweight="bold")
    ax.set_aspect("equal"); ax.axis("off"); ax.legend(fontsize=9, loc="lower left")


def main():
    fig = plt.figure(figsize=(12.0, 5.4))
    ax0 = fig.add_subplot(1, 2, 1, projection="3d")
    ax1 = fig.add_subplot(1, 2, 2)
    surfaces(ax0); deviatoric_plane(ax1)
    fig.suptitle("Tresca and von Mises in principal-stress space. The axis of both is the "
                 "hydrostatic line, which is why pressure never reaches them.",
                 fontsize=11.5, y=0.98)
    plt.tight_layout()
    save(fig, "08_yield_surfaces")


if __name__ == "__main__":
    main()
