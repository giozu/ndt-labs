"""The drawings of module M1.

They live here, beside the notebook, rather than inside it: the plotting code is long,
teaches nothing and made the notebook unreadable on the repository page. The notebook
shows the resulting images; this script is the only owner of them.

    python3 make_figures.py

writes the PNGs the notebook embeds into this folder. If NDT_COURSE_NOTES_FIGURES points
at a directory it also writes the PDF versions there, so the notebook and the course notes
cannot drift apart.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
NOTES = os.environ.get("NDT_COURSE_NOTES_FIGURES", "")


def save(fig, name):
    fig.savefig(os.path.join(HERE, name + ".png"), dpi=110, bbox_inches="tight")
    if os.path.isdir(NOTES):
        fig.savefig(os.path.join(NOTES, name + ".pdf"), bbox_inches="tight")
    plt.close(fig)


def cut_body(ax_a, ax_b):
    """Left: the body under external loads, cut by the plane A. Right: part I alone."""
    # an irregular but reproducible body
    m = 400
    th = np.linspace(0, 2*np.pi, m, endpoint=False)
    r = 1 + 0.18*np.sin(3*th) + 0.11*np.cos(5*th) - 0.07*np.sin(2*th)
    P = np.c_[r*np.cos(th), r*np.sin(th)]

    # External loads. "In equilibrium" is the premise of the whole argument, so the
    # arrows are made to satisfy it rather than merely look like it: project the net
    # force and the net moment out of a random set of loads.
    k = np.arange(0, m, 33)
    p, rng = P[k], np.random.default_rng(3)
    unit = p/np.linalg.norm(p, axis=1)[:, None]
    f = unit*rng.uniform(0.22, 0.42, (len(k), 1)) + 0.10*rng.standard_normal((len(k), 2))
    A = np.zeros((3, 2*len(k)))          # rows: net Fx, net Fy, net moment about O
    A[0, 0::2], A[1, 1::2] = 1, 1
    A[2, 0::2], A[2, 1::2] = -p[:, 1], p[:, 0]
    v = f.ravel()
    v -= A.T @ np.linalg.solve(A @ A.T, A @ v)
    f = v.reshape(-1, 2)
    assert np.abs(A @ v).max() < 1e-12, "the body drawn is not in equilibrium"

    # the cut A-A; part I is the arc i2 -> i1 closed by the chord
    i1, i2 = 30, 200
    a1, a2 = P[i1], P[i2]
    part1 = np.vstack([P[i2:], P[:i1 + 1]])
    O = 0.40*a1 + 0.60*a2                             # the point P, on the cut
    d = (a2 - a1)/np.linalg.norm(a2 - a1)
    nrm = np.array([-d[1], d[0]])
    if nrm @ (part1[len(part1)//2] - O) > 0:
        nrm = -nrm                                    # outward from part I
    on_I = (k >= i2) | (k <= i1)                      # loads that stayed with part I

    for ax in (ax_a, ax_b):
        ax.set_aspect('equal'); ax.axis('off')
        ax.set_xlim(-1.7, 1.9); ax.set_ylim(-1.75, 1.75)

    # --- A ---------------------------------------------------------------
    ax_a.plot(*np.vstack([P, P[:1]]).T, 'k', lw=1.6)
    ax_a.plot(*np.c_[a1, a2], 'k--', lw=1.2)
    for q, sg in ((a1, -1.0), (a2, +1.0)):        # the plane the text calls A
        ax_a.text(*(q + sg*0.17*d + 0.15*nrm), 'A', fontsize=12,
                  ha='center', va='center')
    for pk, fk in zip(p, f):
        ax_a.annotate('', xy=pk + fk, xytext=pk,
                      arrowprops=dict(arrowstyle='-|>', color='k', lw=1.2))
    ax_a.text(-0.30, -0.55, 'I', fontsize=15, style='italic')
    ax_a.text(-0.32, 0.86, 'II', fontsize=15, style='italic')
    # Cauchy's first law, made visible: the same point has two faces, one belonging
    # to each half, with opposite normals and equal and opposite tractions.
    td = (0.62*nrm - 0.34*d); td /= np.linalg.norm(td)
    for sg, ln, lt in ((+1, r'$\mathbf{n}$', r'$\mathbf{t}^{(n)}$'),
                       (-1, r'$-\mathbf{n}$', r'$-\mathbf{t}^{(n)}$')):
        ax_a.annotate('', xy=O + sg*0.26*nrm, xytext=O,
                      arrowprops=dict(arrowstyle='-|>', color='C0', lw=1.5))
        ax_a.text(*(O + sg*0.30*nrm + sg*0.20*d), ln, color='C0', fontsize=12,
                  ha='center', va='center')
        ax_a.annotate('', xy=O + sg*0.42*td, xytext=O,
                      arrowprops=dict(arrowstyle='-|>', color='C3', lw=1.9))
        ax_a.text(*(O + sg*0.50*td - sg*0.26*d), lt, color='C3', fontsize=12,
                  ha='center', va='center')
    ax_a.plot(*O, 'ko', ms=3.5)
    ax_a.annotate('point P', xy=O, xytext=O + [0.78, -0.50], fontsize=10,
                  arrowprops=dict(arrowstyle='-', color='k', lw=0.7))

    # --- B ---------------------------------------------------------------
    ax_b.plot(*np.vstack([part1, part1[:1]]).T, 'k', lw=1.6)
    for pk, fk in zip(p[on_I], f[on_I]):
        ax_b.annotate('', xy=pk + fk, xytext=pk,
                      arrowprops=dict(arrowstyle='-|>', color='k', lw=1.2))
    for s in np.linspace(0.06, 0.94, 12):    # what part II used to apply, distributed
        q = a1 + s*(a2 - a1)
        ax_b.annotate('', xy=q + 0.30*nrm*(0.8 + 0.45*np.sin(3.4*s)), xytext=q,
                      arrowprops=dict(arrowstyle='-|>', color='0.6', lw=0.9))
    dF = 0.62*nrm - 0.34*d                   # deliberately not parallel to n
    ax_b.annotate('', xy=O + dF, xytext=O,
                  arrowprops=dict(arrowstyle='-|>', color='C3', lw=2.2))
    ax_b.text(*(O + dF + [-0.24, 0.05]), r'$d\mathbf{F}$', color='C3', fontsize=13)
    ax_b.annotate('', xy=O + 0.42*nrm, xytext=O,
                  arrowprops=dict(arrowstyle='-|>', color='C0', lw=1.6))
    ax_b.text(*(O + 0.46*nrm + [0.06, 0.02]), r'$\mathbf{n}$', color='C0', fontsize=13)
    # the split the text writes down: a normal part along n, a shear part in the plane
    dFn = (dF @ nrm)*nrm
    dFt = dF - dFn
    for vec, col, lab in ((dFn, 'C2', r'$dF_n$'), (dFt, 'C4', r'$dF_\tau$')):
        ax_b.annotate('', xy=O + vec, xytext=O, zorder=5,
                      arrowprops=dict(arrowstyle='-|>', color=col, lw=1.4, alpha=0.9))
    ax_b.plot(*np.c_[O + dFn, O + dF], ls=':', color='0.5', lw=1.0)
    ax_b.plot(*np.c_[O + dFt, O + dF], ls=':', color='0.5', lw=1.0)
    ax_b.text(*(O + dFt + [0.06, -0.22]), r'$dF_\tau$', color='C4', fontsize=11)
    ax_b.text(*(O + dFn + [-0.32, 0.04]), r'$dF_n$', color='C2', fontsize=11)
    ax_b.plot(*O, 'ko', ms=3.5)
    ax_b.annotate(r'$dA$', xy=O, xytext=O + [0.46, -0.40], fontsize=12,
                  arrowprops=dict(arrowstyle='-', color='k', lw=0.7))
    ax_b.text(-0.30, -0.55, 'I', fontsize=15, style='italic')


def cauchy_tetrahedron(ax):
    U = np.array([[-0.62, 1.00, 0.00],          # 3-D -> 2-D projection
                  [-0.36, -0.26, 1.00]])
    pr = lambda v: U @ np.asarray(v, float)

    a = np.array([1.30, 1.55, 1.30])            # intercepts on the three axes
    V, O = np.diag(a), np.zeros(3)

    cr = np.cross(V[1] - V[0], V[2] - V[0])     # the inclined face
    dA = 0.5*np.linalg.norm(cr)
    n = cr/np.linalg.norm(cr)
    if n @ (V.mean(0) - O) < 0:
        n = -n

    dA_i = np.array([0.5*a[1]*a[2], 0.5*a[0]*a[2], 0.5*a[0]*a[1]])
    assert np.allclose(dA_i, n*dA), "dA_i = n_i dA failed"

    tri = np.array([pr(v) for v in V])
    ax.fill(*tri.T, facecolor='C0', edgecolor='k', lw=1.7, alpha=0.16, zorder=3)
    for k in range(3):
        ax.plot(*np.c_[pr(O), tri[k]], 'k--', lw=1.0, alpha=0.55, zorder=2)
    for k, lab in enumerate(('$x_1$', '$x_2$', '$x_3$')):
        e = np.zeros(3); e[k] = 1
        p = pr(a[k]*e*1.55)
        ax.annotate('', xy=p, xytext=pr(a[k]*e), zorder=1,
                    arrowprops=dict(arrowstyle='-|>', color='k', lw=1.1))
        ax.text(*(p*1.12), lab, fontsize=12, ha='center', va='center')
    for k, lab, sc in ((0, r'$dA_1$', [1.42, 1.18]), (1, r'$dA_2$', [2.05, 0.85]),
                       (2, r'$dA_3$', [1.05, 1.62])):
        mid = (O + V[(k + 1) % 3] + V[(k + 2) % 3])/3
        ax.text(*(pr(mid)*sc), lab, color='0.35', fontsize=12,
                ha='center', va='center', zorder=5)

    C = V.mean(0)
    sig = np.array([[120., 45., -20.], [45., -60., 30.], [-20., 30., 80.]])
    u = (sig @ n)/np.linalg.norm(sig @ n)
    for vec, col, lab, ln in ((n, 'C0', r'$\mathbf{n}$', 0.80),
                              (u, 'C3', r'$\mathbf{t}^{(n)}$', 1.15)):
        p1 = pr(C + ln*vec)
        ax.annotate('', xy=p1, xytext=pr(C), zorder=6,
                    arrowprops=dict(arrowstyle='-|>', color=col, lw=2.3))
        ax.text(*(p1 + 0.13*(p1 - pr(C))), lab, color=col, fontsize=14,
                ha='center', va='center')
    ax.plot(*pr(C), 'ko', ms=3.5, zorder=7)
    ax.text(*(pr(C) + [0.17, -0.20]), '$dA$', fontsize=13, zorder=7)
    ax.plot(*pr(O), 'ko', ms=4, zorder=7)
    ax.text(*(pr(O) + [-0.18, -0.18]), '$P$', fontsize=12)

    # annotations do not extend the data limits, so the axis arrows would be clipped
    pts = np.array([pr(O)] + [pr(v) for v in V]
                   + [pr(a[k]*np.eye(3)[k]*1.75) for k in range(3)]
                   + [pr(C + 1.3*n), pr(C + 1.3*u)])
    ax.set_xlim(pts[:, 0].min() - 0.35, pts[:, 0].max() + 0.35)
    ax.set_ylim(pts[:, 1].min() - 0.30, pts[:, 1].max() + 0.30)
    ax.set_aspect('equal'); ax.axis('off')
    return n, dA, dA_i, sig


def stress_cube(ax):
    """The nine components, on the three visible faces of an element."""
    U = np.array([[-0.56, 1.00, 0.00],
                  [-0.40, -0.22, 1.00]])
    pr = lambda v: U @ np.asarray(v, float)
    # depth direction of this projection: the vertex furthest from the viewer is
    # the one that hides three edges
    w = np.cross(U[0], U[1])
    h = 1.0
    c = np.array([[sx*h, sy*h, sz*h] for sx in (-1, 1) for sy in (-1, 1)
                  for sz in (-1, 1)], float)
    back = int(np.argmin(c @ w))
    edges = [(a, b) for a in range(8) for b in range(a + 1, 8)
             if np.count_nonzero(c[a] != c[b]) == 1]
    for a, b in edges:
        st = '--' if back in (a, b) else '-'
        ax.plot(*np.c_[pr(c[a]), pr(c[b])], st, color='k', lw=1.1,
                alpha=0.55 if st == '--' else 1.0)

    I = np.eye(3)
    names = [('x', '1'), ('y', '2'), ('z', '3')]
    for k in range(3):                       # the three visible faces, normal +e_k
        ctr = I[k]*h
        ax.plot(*pr(ctr), 'o', color='0.3', ms=3, zorder=6)
        for m in range(3):
            v = I[(k + m) % 3]*(0.92, 0.70, 0.92)[m]
            p0, p1 = pr(ctr), pr(ctr + v)
            col = 'C3' if m == 0 else '0.2'
            ax.annotate('', xy=p1, xytext=p0, zorder=5,
                        arrowprops=dict(arrowstyle='-|>', color=col,
                                        lw=1.7 if m == 0 else 1.2))
            j_ = (k + m) % 3
            # short labels only: the tau_xy <-> sigma_12 dictionary is in the array
            # above the figure, and spelling both out here gives nine labels that
            # collide with one another in this projection
            if m == 0:
                lab = f"$\\sigma_{{{names[k][1]}{names[k][1]}}}$"
            else:
                lab = f"$\\tau_{{{names[k][1]}{names[j_][1]}}}$"
            d = (p1 - p0)/np.linalg.norm(p1 - p0)
            perp = np.array([-d[1], d[0]])
            if perp @ p1 < 0:                # always push the label outwards
                perp = -perp
            ax.text(*(p1 + 0.12*d + 0.17*perp), lab, fontsize=11, color=col,
                    ha='center', va='center', zorder=6,
                    bbox=dict(fc='white', ec='none', alpha=0.9, pad=0.8))

    # the normal stress on face k points along +e_k, i.e. along the axis itself, so the
    # axis label has to be pushed clear of it
    for k, lab in enumerate(('$x_1$', '$x_2$', '$x_3$')):
        e = I[k]
        p = pr(2.75*e)
        ax.annotate('', xy=p, xytext=pr(1.7*e), zorder=1,
                    arrowprops=dict(arrowstyle='-|>', color='k', lw=1.0))
        ax.text(*(p*1.16), lab, fontsize=12, ha='center', va='center')

    pts = np.array([pr(v) for v in c] + [pr(2.9*I[k]) for k in range(3)]
                   + [pr(I[k]*h + I[(k + m) % 3]*1.3) for k in range(3) for m in range(3)])
    ax.set_xlim(pts[:, 0].min() - 0.55, pts[:, 0].max() + 0.55)
    ax.set_ylim(pts[:, 1].min() - 0.40, pts[:, 1].max() + 0.40)
    ax.set_aspect('equal'); ax.axis('off')


def moment_balance(ax):
    """Why the shears pair up: moments about the centre of a plane element."""
    a = 1.0
    ax.plot([-a, a, a, -a, -a], [-a, -a, a, a, -a], 'k', lw=1.4)
    for (x0, y0, dx, dy, lab, lp) in [
            ( a,  0,  0,  0.75, r'$\tau_{12}$', ( a+0.30,  0.45)),
            (-a,  0,  0, -0.75, r'$\tau_{12}$', (-a-0.36, -0.50)),
            ( 0,  a,  0.75, 0,  r'$\tau_{21}$', ( 0.45,  a+0.28)),
            ( 0, -a, -0.75, 0,  r'$\tau_{21}$', (-0.50, -a-0.32))]:
        ax.annotate('', xy=(x0+dx, y0+dy), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle='-|>', color='C0', lw=2.0))
        ax.text(*lp, lab, color='C0', fontsize=13, ha='center', va='center')
    ax.annotate('', xy=(a, -a - 0.78), xytext=(-a, -a - 0.78),
                arrowprops=dict(arrowstyle='<->', color='0.5', lw=0.9))
    ax.text(0, -a - 1.08, r'$dx_1$', fontsize=11, ha='center', color='0.35')
    ax.annotate('', xy=(-a - 0.85, a), xytext=(-a - 0.85, -a),
                arrowprops=dict(arrowstyle='<->', color='0.5', lw=0.9))
    ax.text(-a - 1.12, 0, r'$dx_2$', fontsize=11, va='center', ha='center', color='0.35')
    ax.set_xlim(-2.7, 2.3); ax.set_ylim(-2.5, 2.1)
    ax.set_aspect('equal'); ax.axis('off')


# --------------------------------------------------------------------------------
# Shared machinery for the two axonometric cube drawings below.
#
# 01_stress_transformation redraws, from scratch, the same statement as the figure
# "Stress transformation 3D" on Wikipedia: nothing is copied, the drawing is ours, and
# the palette is the one a reader coming from that article will recognise.
_U = np.array([[-0.56, 1.00, 0.00],
               [-0.40, -0.22, 1.00]])
_pr = lambda v: _U @ np.asarray(v, float)
_W = np.cross(_U[0], _U[1])                    # points towards the viewer
_FACE = ('#E66C4C', '#FDEA87', '#FA9E39')      # the faces normal to e_1, e_2, e_3
_RED, _BLUE = '#FF3030', '#317DAF'


def _cube(ax, keep, o, B, h, prime=False, fs=9.5, arr=0.52):
    """A cube centred on o, its own axes the rows of B, carrying sigma_kj on each
    visible face: three arrows from the face centre along e_1, e_2, e_3."""
    o = np.asarray(o, float); B = np.asarray(B, float)
    sg = [(a, b, c) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
    V = [o + h*(s[0]*B[0] + s[1]*B[1] + s[2]*B[2]) for s in sg]
    keep(*[_pr(v) for v in V])
    for k in range(3):
        for s in (+1, -1):
            if (s*B[k]) @ _W <= 0:             # facing away: not drawn
                continue
            idx = [i for i, t in enumerate(sg) if t[k] == s]
            ctr = _pr(o + s*h*B[k])
            idx.sort(key=lambda i: np.arctan2(*(_pr(V[i]) - ctr)[::-1]))
            ax.add_patch(Polygon([_pr(V[i]) for i in idx], closed=True,
                                 fc=_FACE[k], ec='k', lw=1.3, zorder=3))
    back = int(np.argmin([v @ _W for v in V]))
    for a in range(8):
        for b in range(a + 1, 8):
            if sum(x != y for x, y in zip(sg[a], sg[b])) == 1 and back in (a, b):
                ax.plot(*np.c_[_pr(V[a]), _pr(V[b])], '--', color='0.5', lw=0.8, zorder=2)
    m = "'" if prime else ""
    for k in range(3):
        if B[k] @ _W <= 0:
            continue
        c0 = o + h*B[k]
        for j in range(3):
            tip = c0 + arr*h*B[j]
            ax.annotate('', xy=_pr(tip), xytext=_pr(c0), zorder=6,
                        arrowprops=dict(arrowstyle='-|>', color='k', lw=1.4,
                                        shrinkA=0, shrinkB=0, mutation_scale=11))
            d = _pr(tip) - _pr(c0); d /= np.linalg.norm(d)
            perp = np.array([-d[1], d[0]])
            if perp @ (_pr(c0) - _pr(o)) < 0:  # push the label away from the body
                perp = -perp
            q = _pr(tip) + 0.20*d + 0.17*perp
            keep(q)
            ax.text(*q, rf"$\sigma{m}_{{{k+1}{j+1}}}$", fontsize=fs, ha='center',
                    va='center', zorder=7,
                    bbox=dict(fc='white', ec='none', alpha=0.82, pad=0.4))


def _triad(ax, keep, L, B, colour, names, fs=13, lw=1.5):
    for k in range(3):
        p = _pr(L*np.asarray(B)[k]); keep(p, p*1.17)
        ax.annotate('', xy=p, xytext=(0, 0), zorder=4,
                    arrowprops=dict(arrowstyle='-|>', color=colour, lw=lw,
                                    shrinkA=0, shrinkB=0, mutation_scale=13))
        ax.text(*(p*1.12), names[k], color=colour, fontsize=fs,
                ha='center', va='center', zorder=8)


def _arc(ax, keep, u, v, r, label, fs=11.5, off=0.30, rad=0.30):
    """A double-headed arc between two axes, labelled with its direction cosine."""
    a, b = _pr(r*np.asarray(u)), _pr(r*np.asarray(v))
    ax.add_patch(FancyArrowPatch(a, b, connectionstyle=f'arc3,rad={rad}',
                                 arrowstyle='<|-|>', mutation_scale=10,
                                 color=_BLUE, lw=1.2, zorder=5, shrinkA=0, shrinkB=0))
    # arc3 puts the control point at mid + rad*perp, so the curve's midpoint is at
    # mid + rad/2*perp; every arc here is centred on the origin, so the label is
    # pushed radially outwards from there
    mid = 0.5*(a + b); perp = np.array([-(b - a)[1], (b - a)[0]])
    cmid = mid + 0.5*rad*perp
    q = cmid*(1 + off/np.linalg.norm(cmid)); keep(q)
    ax.text(*q, label, color='k', fontsize=fs, ha='center', va='center', zorder=8,
            bbox=dict(fc='white', ec='none', alpha=0.85, pad=0.5))


def _primed_basis(t=0.45, s=0.60):
    """A rotated orthonormal triad, chosen for how it reads on the page: x'_3 above and
    right of x_3, x'_1 above x_1, x'_2 below x_2. Orthonormal and right-handed."""
    I = np.eye(3)
    n = lambda v: v/np.linalg.norm(v)
    e3 = n(I[2] + t*I[1])
    e1 = n(I[0] + s*I[2]); e1 = n(e1 - (e1 @ e3)*e3)
    return np.array([e1, np.cross(e3, e1), e3])


def stress_transformation(ax_a, ax_b):
    """The same nine components seen from two orthogonal frames.

    Left: sigma_ij in (x_1, x_2, x_3), the first index naming the face. Right: the same
    state read in a rotated frame, with the direction cosines a_ij = e'_i . e_j that
    carry one into the other through sigma' = Q sigma Q^T.
    """
    I = np.eye(3)
    for ax, build in ((ax_a, 'a'), (ax_b, 'b')):
        pts = []
        keep = lambda *p: pts.extend(np.asarray(q, float) for q in p)
        if build == 'a':
            _triad(ax, keep, 3.2, I, 'k', ('$x_1$', '$x_2$', '$x_3$'))
            _cube(ax, keep, [-0.30, 1.95, 1.60], I, 1.10, fs=10)
        else:
            Q = _primed_basis()
            _triad(ax, keep, 2.7, I, 'k', ('$x_1$', '$x_2$', '$x_3$'), fs=12, lw=1.2)
            _triad(ax, keep, 3.0, Q, _RED, ("$x'_1$", "$x'_2$", "$x'_3$"), fs=13, lw=1.7)
            _arc(ax, keep, Q[0], I[2], 1.85, r'$\cos^{-1}a_{13}$')
            _arc(ax, keep, I[2], Q[2], 1.70, r'$\cos^{-1}a_{33}$', off=0.95)
            _arc(ax, keep, I[0], Q[1], 1.85, r'$\cos^{-1}a_{21}$')
            _cube(ax, keep, 3.1*Q[1] + 3.0*Q[2] - 0.6*Q[0], Q, 1.10, prime=True, fs=9.5)
        P = np.array(pts)
        ax.set_xlim(P[:, 0].min() - 0.35, P[:, 0].max() + 0.35)
        ax.set_ylim(P[:, 1].min() - 0.35, P[:, 1].max() + 0.35)
        ax.set_aspect('equal'); ax.axis('off')


def equilibrium_cube(ax, h=1.0):
    """The six faces of an element, and why opposite faces do not cancel.

    Each face carries sigma_kj, the index j left free exactly as the text writes it.
    The three faces at +dx_k/2 are drawn solid and tinted and carry the value at the
    far face; the three at -dx_k/2 are dashed and carry sigma_kj itself. The difference
    between the two, per unit length, is the derivative in the equilibrium equations.
    """
    COL = ('#C1272D', '#1E8449', '#1F5FA8')       # components on faces 1, 2, 3
    BODY = '#8E44AD'
    I = np.eye(3)
    pts = []
    keep = lambda *p: pts.extend(np.asarray(q, float) for q in p)

    sg = [(a, b, c) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
    V = [h*np.array(t, float) for t in sg]
    keep(*[_pr(v) for v in V])
    for k in range(3):                             # a light tint on the visible faces
        if I[k] @ _W <= 0:
            continue
        idx = [i for i, t in enumerate(sg) if t[k] == 1]
        c2 = _pr(h*I[k])
        idx.sort(key=lambda i: np.arctan2(*(_pr(V[i]) - c2)[::-1]))
        ax.add_patch(Polygon([_pr(V[i]) for i in idx], closed=True, fc=COL[k],
                             ec='none', alpha=0.10, zorder=0))
    back = int(np.argmin([v @ _W for v in V]))
    for a in range(8):
        for b in range(a + 1, 8):
            if sum(x != y for x, y in zip(sg[a], sg[b])) == 1:
                hid = back in (a, b)
                ax.plot(*np.c_[_pr(V[a]), _pr(V[b])], '--' if hid else '-',
                        color='0.55' if hid else 'k', lw=0.9 if hid else 1.4,
                        zorder=1 if hid else 4)

    for k in range(3):
        for s_ in (+1, -1):
            ctr = s_*h*I[k]
            vis = (s_*I[k]) @ _W > 0
            ax.plot(*_pr(ctr), 'o', color=COL[k], ms=3.5, zorder=6)
            for j in range(3):
                tip = ctr + s_*0.62*h*I[j]
                ax.annotate('', xy=_pr(tip), xytext=_pr(ctr), zorder=6,
                            arrowprops=dict(arrowstyle='-|>', color=COL[k],
                                            lw=1.5 if vis else 1.0,
                                            alpha=1.0 if vis else 0.55,
                                            linestyle='-' if vis else (0, (3, 2)),
                                            shrinkA=0, shrinkB=0, mutation_scale=10))
            anchor = _pr(ctr); out = anchor/np.linalg.norm(anchor)
            if vis:
                lab = (rf"$\sigma_{{{k+1}j}}+\dfrac{{\partial\sigma_{{{k+1}j}}}}"
                       rf"{{\partial x_{k+1}}}\,dx_{k+1}$")
                q = anchor + 1.45*out
                ax.annotate('', xy=q, xytext=anchor, zorder=2,
                            arrowprops=dict(arrowstyle='-', color=COL[k], lw=0.8,
                                            alpha=0.65, shrinkA=5, shrinkB=5))
                fs = 11
            else:
                lab, q, fs = rf"$\sigma_{{{k+1}j}}$", anchor + 0.30*out, 12
            keep(q, q + 0.8*out)
            ax.text(*q, lab, color=COL[k], fontsize=fs, ha='center', va='center',
                    zorder=7, bbox=dict(fc='white', ec='none', alpha=0.9, pad=1.0))

    # the body force: one vector through the centre, not three, so that it does not
    # compete with the face triads for the middle of the drawing
    d3 = np.array([0.45, 0.30, 0.62]); d3 /= np.linalg.norm(d3)
    tip = 0.62*h*d3
    ax.annotate('', xy=_pr(tip), xytext=(0, 0), zorder=8,
                arrowprops=dict(arrowstyle='-|>', color=BODY, lw=2.0,
                                shrinkA=0, shrinkB=0, mutation_scale=12))
    d = _pr(tip)/np.linalg.norm(_pr(tip))
    ax.text(*(_pr(tip) + 0.24*d), r"$\mathbf{b}$", color=BODY, fontsize=12,
            ha='center', va='center', zorder=9,
            bbox=dict(fc='white', ec='none', alpha=0.85, pad=0.4))

    org = np.array([-2.6, -1.9])                   # a detached orientation triad
    for j, nm in enumerate(('$x_1$', '$x_2$', '$x_3$')):
        t2 = org + 0.72*_pr(I[j])
        ax.annotate('', xy=t2, xytext=org, zorder=8,
                    arrowprops=dict(arrowstyle='-|>', color='k', lw=1.2,
                                    shrinkA=0, shrinkB=0, mutation_scale=10))
        d = (t2 - org)/np.linalg.norm(t2 - org)
        keep(t2 + 0.45*d)
        ax.text(*(t2 + 0.22*d), nm, fontsize=11, ha='center', va='center', zorder=9)
    keep(org)

    P = np.array(pts)
    ax.set_xlim(P[:, 0].min() - 0.5, P[:, 0].max() + 0.5)
    ax.set_ylim(P[:, 1].min() - 0.4, P[:, 1].max() + 0.4)
    ax.set_aspect('equal'); ax.axis('off')


def main():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 5.4))
    cut_body(a, b)
    fig.tight_layout()
    save(fig, "01_traction")

    fig, ax = plt.subplots(figsize=(7.0, 6.0))
    cauchy_tetrahedron(ax)
    fig.tight_layout()
    save(fig, "01_tetrahedron")

    fig, (a, b) = plt.subplots(1, 2, figsize=(12.6, 5.6),
                               gridspec_kw={"width_ratios": [1.35, 1]})
    stress_cube(a)
    moment_balance(b)
    fig.tight_layout()
    save(fig, "01_stress_cube")

    fig, (a, b) = plt.subplots(1, 2, figsize=(13.2, 5.8))
    stress_transformation(a, b)
    fig.tight_layout()
    save(fig, "01_stress_transformation")

    fig, ax = plt.subplots(figsize=(9.2, 6.4))
    equilibrium_cube(ax)
    fig.tight_layout()
    save(fig, "01_equilibrium_cube")

    print("written:", ", ".join(sorted(f for f in os.listdir(HERE)
                                       if f.endswith(".png"))))


if __name__ == "__main__":
    main()
