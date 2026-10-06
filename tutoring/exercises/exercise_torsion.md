# Exercise: torsion of a thin-walled tube

A thin-walled steel tube is twisted by a torque $T$ about its axis $z$.

| data | value |
|---|---|
| mean radius | $R = 20$ mm |
| wall thickness | $t = 2$ mm |
| length | $L = 200$ mm |
| torque | $T = 300$ N m |
| steel S235 | $S_y = 235$ MPa, $E = 200$ GPa, $\nu = 0.3$ |
| grey cast iron, for questions 4 and 5 | $\sigma_{ut} = 210$ MPa, $\sigma_{uc} = 510$ MPa |

Stresses are positive in tension. On the wall, use the local frame $(r, \theta, z)$: $r$ radial, $\theta$ along the circumference, $z$ along the axis.

## Questions

1. Compute the shear stress in the wall and write the stress tensor.
2. Take a plane on the wall whose normal $\mathbf n$ is at an angle $\alpha$ from the axis $z$. Compute $\sigma_n$ and $\tau_n$, find the principal stresses and their directions, and draw Mohr's circle. Compare with uniaxial tension.
3. Compute the shear strain, the angle of twist and the principal strains. Does the volume change?
4. At what torque does the tube yield, by Tresca and by von Mises? What are the safety factors at $T = 300$ N m? At what torque would a cast-iron tube break?
5. How does a steel shaft break in torsion, and how does a cast-iron one?

---

## Solution

### 1. Stress

The shear $\tau$ acts on the ring of area $2\pi R t$, at lever arm $R$. Moment equilibrium:

```math
T = \tau\,(2\pi R t)\,R
\quad\Rightarrow\quad
\tau = \frac{T}{2\pi R^2 t} = \frac{300\cdot10^3}{2\pi\cdot 20^2\cdot 2} = 59.7\ \text{MPa}
```

For $t \ll R$ (here $t/R = 0.1$) the stress is uniform through the wall. In the frame $(z, \theta)$ of the wall the only non-zero components are $\sigma_{\theta z} = \sigma_{z\theta} = \tau$, and $\sigma_{rr} = 0$ because the surfaces of the wall are free:

```math
\boldsymbol\sigma =
\begin{pmatrix}
0 & \tau \\
\tau & 0
\end{pmatrix}
\qquad (z, \theta)
```

This is **pure shear**.

### 2. Inclined plane, principal stresses, Mohr's circle

The normal and the tangent of the plane, with $\mathbf m$ obtained by turning $\mathbf n$ by $-90°$:

```math
\mathbf n = (\cos\alpha,\ \sin\alpha), \qquad
\mathbf m = (\sin\alpha,\ -\cos\alpha), \qquad
\mathbf t = \boldsymbol\sigma\,\mathbf n = (\tau\sin\alpha,\ \tau\cos\alpha)
```

```math
\sigma_n = \mathbf t\cdot\mathbf n = \tau\sin 2\alpha, \qquad
\tau_n = \mathbf t\cdot\mathbf m = -\tau\cos 2\alpha
```

| $\alpha$ | plane | $\sigma_n$ | $\tau_n$ |
|:---:|:---|:---:|:---:|
| 0° | cross-section | 0 | $-\tau$ |
| 45° | helix | $+\tau$ | 0 |
| 90° | longitudinal cut | 0 | $+\tau$ |
| 135° | helix | $-\tau$ | 0 |

**Principal stresses.** The eigenvalues of the tensor:

```math
\det\begin{pmatrix} -\lambda & \tau \\ \tau & -\lambda \end{pmatrix} = \lambda^2 - \tau^2 = 0
\quad\Rightarrow\quad \lambda = \pm\tau
```

so $\sigma_1 = +\tau$ along $(1, 1)/\sqrt2$, at $+45°$ from the axis, and $\sigma_3 = -\tau$ along $(1, -1)/\sqrt2$, at $-45°$; the third, $\sigma_2 = \sigma_{rr} = 0$, is normal to the wall. The principal directions run along two helices. Pure shear **is** a tension $\tau$ and a compression $\tau$ at right angles, turned by 45°.

**Mohr's circle.** Centre at the origin, radius $\tau$. Each point is a plane: the cross-section ($\alpha = 0$) is the point $(0, -\tau)$ at the bottom, because it carries shear only and is not a principal plane; turning the plane by $\alpha$ moves the point by $2\alpha$ anticlockwise, reaching $\sigma_1 = +\tau$ on the right at $\alpha = 45°$. This is the largest of the three circles of the state, the one of the pair $(\sigma_1, \sigma_3)$, and its radius is the largest shear, $\tau_{\max} = \tau$.

**Against uniaxial tension:**

| | tension | torsion |
|:---|:---:|:---:|
| principal stresses | $\sigma$, 0, 0 | $\tau$, 0, $-\tau$ |
| centre of the circle | $\sigma/2$ | 0 |
| the cross-section on the circle | $(\sigma, 0)$, a principal plane | $(0, -\tau)$, pure shear |
| largest shear | $\sigma/2$, at 45° | $\tau$, on the cross-section |
| largest normal stress | $\sigma$, on the cross-section | $\tau$, at 45° |

The two critical planes swap places.

### 3. Strains

```math
G = \frac{E}{2(1+\nu)} = 76.9\ \text{GPa}, \qquad
\gamma = \frac{\tau}{G} = 7.76\cdot10^{-4}, \qquad
\varphi = \frac{\gamma L}{R} = 7.76\cdot10^{-3}\ \text{rad} = 0.44°
```

$\varphi$ is the relative rotation of the two ends: a straight line drawn along the tube becomes a helix inclined by $\gamma$.

The principal strains are at 45°, $\varepsilon_1 = +\gamma/2$ and $\varepsilon_3 = -\gamma/2$: Mohr's circle of strain is centred at the origin with radius $\gamma/2$. This is why a strain gauge bonded at 45° on a shaft measures its torque.

The volume does not change, $\varepsilon_v = \varepsilon_1 + \varepsilon_3 = 0$: pure shear changes the shape only. In uniaxial tension, instead, $\varepsilon_v = (1-2\nu)\sigma/E > 0$.

### 4. Yield and fracture

With $\sigma_1 = \tau$ and $\sigma_3 = -\tau$:

```math
\text{Tresca: } 2\tau \le S_y \;\Rightarrow\; \tau_y = \frac{S_y}{2}, \qquad
\text{von Mises: } \sqrt3\,\tau \le S_y \;\Rightarrow\; \tau_y = \frac{S_y}{\sqrt3}, \qquad
\text{Galileo-Rankine: } \tau \le \sigma_{ut}
```

| criterion | critical $\tau$ (MPa) | critical $T = \tau\cdot 2\pi R^2 t$ (N m) | $\varphi$ at the limit | safety factor at $T = 300$ N m |
|:---|:---:|:---:|:---:|:---:|
| Tresca | 117.5 | **591** | 0.88° | **1.97** |
| von Mises | 135.7 | **682** | 1.01° | **2.27** |
| cast iron, Galileo-Rankine | 210 | **1056** | 1.56° | 3.52 |

The ratio of the two yield criteria is $2/\sqrt3 = 1.155$: in pure shear Tresca and von Mises are 15 % apart, the most they can ever differ. For cast iron $\sigma_3 = -210$ MPa stays well above $-\sigma_{uc} = -510$ MPa, so tension governs.

### 5. How it breaks

- A **ductile** steel shaft slips where the shear is largest: on the **cross-section**. It breaks flat, straight across.
- A **brittle** cast-iron shaft opens where the normal stress is largest: at **45°**. It breaks along a helix.

Exactly the reverse of uniaxial tension, where the ductile bar slips at 45° and the brittle one breaks flat. Try it with a piece of chalk: twisted, it breaks along a helix; bent, straight across.
