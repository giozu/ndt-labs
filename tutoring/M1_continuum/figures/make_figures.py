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

    for k, lab in enumerate(('$x$', '$y$', '$z$')):
        e = I[k]
        p = pr(2.5*e)
        ax.annotate('', xy=p, xytext=pr(1.7*e), zorder=1,
                    arrowprops=dict(arrowstyle='-|>', color='k', lw=1.0))
        ax.text(*(p*1.10), lab, fontsize=12, ha='center', va='center')

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
            ( a,  0,  0,  0.75, r'$\tau_{xy}$', ( a+0.30,  0.45)),
            (-a,  0,  0, -0.75, r'$\tau_{xy}$', (-a-0.36, -0.50)),
            ( 0,  a,  0.75, 0,  r'$\tau_{yx}$', ( 0.45,  a+0.28)),
            ( 0, -a, -0.75, 0,  r'$\tau_{yx}$', (-0.50, -a-0.32))]:
        ax.annotate('', xy=(x0+dx, y0+dy), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle='-|>', color='C0', lw=2.0))
        ax.text(*lp, lab, color='C0', fontsize=13, ha='center', va='center')
    ax.annotate('', xy=(a, -a - 0.78), xytext=(-a, -a - 0.78),
                arrowprops=dict(arrowstyle='<->', color='0.5', lw=0.9))
    ax.text(0, -a - 1.08, r'$dx$', fontsize=11, ha='center', color='0.35')
    ax.annotate('', xy=(-a - 0.85, a), xytext=(-a - 0.85, -a),
                arrowprops=dict(arrowstyle='<->', color='0.5', lw=0.9))
    ax.text(-a - 1.12, 0, r'$dy$', fontsize=11, va='center', ha='center', color='0.35')
    ax.set_xlim(-2.7, 2.3); ax.set_ylim(-2.5, 2.1)
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

    print("written:", ", ".join(sorted(f for f in os.listdir(HERE)
                                       if f.endswith(".png"))))


if __name__ == "__main__":
    main()
