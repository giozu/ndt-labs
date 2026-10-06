# Exercise: uniaxial tension of a round bar

A round steel bar is pulled along its axis $z$.

| data | value |
|---|---|
| diameter | $d = 10$ mm |
| gauge length | $L_0 = 50$ mm |
| axial force | $F = 15$ kN |
| steel S235 | $S_y = 235$ MPa, $E = 200$ GPa, $\nu = 0.3$ |
| grey cast iron, for question 6 | $\sigma_{ut} = 210$ MPa, $\sigma_{uc} = 510$ MPa |

Stresses are positive in tension.

## Questions

1. Compute the axial stress and write the stress tensor.
2. Take a plane whose normal $\mathbf n$ is at an angle $\theta$ from the axis $z$. Compute the normal stress $\sigma_n$ and the shear stress $\tau$ on it, and evaluate them at $\theta = 0°$, $30°$, $45°$, $60°$ and $90°$. Where is the shear largest?
3. Draw Mohr's circle of the stress state.
4. Compute the axial, lateral and volumetric strains, the elongation $\Delta L$ and the change of diameter $\Delta d$.
5. At what force does the bar start to yield? Compare Tresca and von Mises.
6. On which plane does a ductile steel bar slip, and on which plane does a cast-iron bar break?

---

## Solution

### 1. Stress

```math
A = \frac{\pi d^2}{4} = 78.5\ \text{mm}^2, \qquad
\sigma = \frac{F}{A} = 191\ \text{MPa}
```

In the frame $(z, x, y)$, with $z$ along the axis, only the axial component is non-zero:

```math
\boldsymbol\sigma =
\begin{pmatrix}
\sigma & 0 & 0 \\
0 & 0 & 0 \\
0 & 0 & 0
\end{pmatrix}
```

The frame is principal: $\sigma_1 = \sigma$, $\sigma_2 = \sigma_3 = 0$.

### 2. Stresses on an inclined plane

The plane contains the transverse direction $y$; in the $(z, x)$ plane its normal and its tangent are

```math
\mathbf n = (\cos\theta,\ \sin\theta), \qquad
\mathbf m = (\sin\theta,\ -\cos\theta)
```

with $\mathbf m$ obtained by turning $\mathbf n$ by $-90°$. Cauchy's law gives the traction on the plane, $\mathbf t = \boldsymbol\sigma^T\mathbf n = (\sigma\cos\theta,\ 0)$, and its two components are

```math
\sigma_n = \mathbf t\cdot\mathbf n = \sigma\cos^2\theta, \qquad
\tau = \mathbf t\cdot\mathbf m = \sigma\sin\theta\cos\theta = \frac{\sigma}{2}\sin 2\theta
```

| $\theta$ | plane | $\sigma_n$ (MPa) | $\tau$ (MPa) |
|:---:|:---|:---:|:---:|
| 0° | cross-section | 191 | 0 |
| 30° | | 143 | 82.7 |
| 45° | | 95.5 | **95.5** $= \sigma/2$ |
| 60° | | 47.7 | 82.7 |
| 90° | longitudinal cut | 0 | 0 |

The shear is largest at $\theta = 45°$, where it equals $\sigma/2$. On the longitudinal cut nothing acts: the bar is pulled along $z$, and that plane is parallel to the load.

### 3. Mohr's circle

With $\sigma_1 = \sigma$ and $\sigma_3 = 0$:

```math
c = \frac{\sigma_1 + \sigma_3}{2} = \frac{\sigma}{2}, \qquad
R = \frac{\sigma_1 - \sigma_3}{2} = \frac{\sigma}{2}, \qquad
\tau_{\max} = R = \frac{\sigma}{2}
```

The circle passes through the origin. Each point is a plane: the cross-section ($\theta = 0$) is the point $(\sigma, 0)$ on the right, a principal plane; turning the plane by $\theta$ moves the point by $2\theta$ anticlockwise, to the top at $\theta = 45°$ and to the origin at $\theta = 90°$.

### 4. Strains

From Hooke's law, with nothing restraining the lateral contraction:

```math
\varepsilon_z = \frac{\sigma}{E} = 9.55\cdot10^{-4}, \qquad
\varepsilon_x = \varepsilon_y = -\nu\,\frac{\sigma}{E} = -2.86\cdot10^{-4}
```

```math
\varepsilon_v = \varepsilon_x + \varepsilon_y + \varepsilon_z = (1-2\nu)\,\frac{\sigma}{E} = 3.8\cdot10^{-4}
```

```math
\Delta L = \varepsilon_z L_0 = 0.048\ \text{mm}, \qquad
\Delta d = \varepsilon_x\, d = -0.0029\ \text{mm}
```

The volume grows: in the elastic range it is not conserved, because $\nu = 0.3$ and not $0.5$.

### 5. Yield

Both criteria reduce to the axial stress:

```math
\text{Tresca: } \sigma_1 - \sigma_3 = \sigma, \qquad
\text{von Mises: } \sqrt{\tfrac12\left[(\sigma_1-\sigma_2)^2 + (\sigma_2-\sigma_3)^2 + (\sigma_3-\sigma_1)^2\right]} = \sigma
```

so the bar yields when $\sigma = S_y$:

```math
F_y = S_y A = 18.5\ \text{kN}
```

In uniaxial tension Tresca and von Mises coincide, because both are calibrated on this very test.

### 6. Where it gives way

- A **ductile** steel bar slips where the shear is largest: on the planes at $\theta = 45°$.
- A **brittle** cast-iron bar opens where the normal stress is largest: on the cross-section, $\theta = 0°$, and breaks flat. Its criterion is Galileo-Rankine, $\sigma_1 \le \sigma_{ut}$ and $\sigma_3 \ge -\sigma_{uc}$; here it breaks at $\sigma = \sigma_{ut} = 210$ MPa, that is $F = \sigma_{ut} A = 16.5$ kN.
