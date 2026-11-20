#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# --.. ..- .-.. .-.. --- Z3ST non-regression script --.. ..- .-.. .-.. ---
"""
NDT course case: LINED, gamma-heated cylinder, thermo-mechanical
Here the wall is BEHIND THE SHIELD: G5_lined_wall with the source q0 exp(-mu t_s) and h_out on
the wetted surface. The reference reads both from the case files, so the check is the same.
Author: Giovanni Zullo

The G4 case (G4_lined_wall_thermal) with the mechanics on: internal pressure P on the
wetted surface, the closed-end axial load on the top face, axial restraint at the bottom.

Reference, independent of the finite elements:
 - temperature: the same K0 gamma source z3st uses, integrated radially by quadrature through
   the two layers (as in G4_lined_wall_thermal);
 - stresses: the composite cylinder in generalised plane strain. In each layer
       u(r) = (1+nu)/(1-nu) alpha/r int dT s ds + C1 r + C2/r,     eps_z uniform,
   which satisfies equilibrium because a uniform eps_z adds the same constant to sigma_rr and
   sigma_tt. Five unknowns (C1, C2 per layer, eps_z), five conditions: sigma_rr(Rw) = -P,
   sigma_rr(Ro) = 0, u and sigma_rr continuous at Ri, axial force = P pi Rw^2 (closed end).

A node on the interface holds the value of one material only (the one listed last in
input.yaml), so a profile through the last liner cell blends the two: the profiles are compared
away from the interface, and the stress at the vessel inner surface is read from the VESSEL cell
next to it.

Writes output/non-regression.json and output/verification.png
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml
from scipy.integrate import cumulative_trapezoid
from scipy.special import k0

from z3st.utils.utils_verification import pass_fail_check, regression_check

import pyvista as pv

CASE_DIR = os.path.dirname(os.path.abspath(__file__))
VTU_FILE = os.path.join(CASE_DIR, "output", "fields.vtu")
OUT_JSON = os.path.join(CASE_DIR, "output", "non-regression.json")

def _yaml(name):
    with open(os.path.join(CASE_DIR, name)) as f:
        return yaml.safe_load(f)

# reading geometry.yaml
geom = _yaml("geometry.yaml")
Rw = float(geom["inner_radius"])        # wetted surface (liner inner face)
Ri = float(geom["interface_radius"])    # liner-vessel interface
Ro = float(geom["outer_radius"])        # vessel outer surface
Lz = float(geom["Lz"])

# reading the two material cards, as listed in input.yaml
materials = _yaml("input.yaml")["materials"]
L = _yaml(materials["liner"])
V = _yaml(materials["steel"])

# gamma source: one profile across the whole wall, so the two cards must agree
mu = float(V["mu_gamma"])
q0 = float(V["gamma_heating"])
assert float(L["mu_gamma"]) == mu, "liner and vessel must have the same mu_gamma"
assert float(L["gamma_heating"]) == q0, "liner and vessel must have the same gamma_heating"

# stress-free temperature: one for both layers
T_REF = float(V["T_ref"])
assert float(L["T_ref"]) == T_REF, "liner and vessel must have the same T_ref"

# reading boundary_conditions.yaml
bcs = _yaml("boundary_conditions.yaml")

# thermal
# wetted surface (liner): convection to the coolant
bc_in = bcs["thermal"]["liner"][0]
H1 = float(bc_in["h_conv"])
T_COOL = float(bc_in["T_ext"])

# outer surface (steel): insulation + containment water
bc_out = bcs["thermal"]["steel"][0]
U2 = float(bc_out["h_conv"])
T_INF = float(bc_out["T_ext"])

# mechanical
# wetted surface (liner): internal pressure
bc_p = bcs["mechanical"]["liner"][0]
P = -float(bc_p["traction"])

# top face (steel): closed-end axial load
bc_top = bcs["mechanical"]["steel"][0]
top_load = float(bc_top["traction"])

closed_end = P*Rw**2/(Ro**2 - Rw**2)
assert abs(top_load/closed_end - 1) < 1e-5, "top load is not the closed-end one"

TOLERANCE = 1.0e-2
I_RR, I_TT, I_ZZ = 0, 4, 8          # (r, theta, z): 4 is the HOOP component, 8 is axial

# --.. ..- .-.. .-.. --- reference temperature (two layers, K0 source) --.. ..- .-.. .-.. ---
# Steady conduction with a source:   d/dr (k r dT/dr) = -q r
# Integrated once from the wetted surface:   k r dT/dr = F - Q(r)
#   Q(r) = int_Rw^r q r' dr'    the heat generated between Rw and r (per radian and metre)
#   F    = k r dT/dr at Rw      the heat leaving through the wetted surface (unknown)
# Integrated again:   T(r) = Tw + F J1(r) - J2(r),   J1 = int dr/(k r),   J2 = int Q/(k r) dr
# The two unknowns, Tw = T(Rw) and F, are fixed by the convection on the two faces.

# radial grid: the liner and the vessel, each with its own points
s = np.unique(np.concatenate([np.linspace(Rw, Ri, 4001), np.linspace(Ri, Ro, 40001)]))
k_s = np.where(s < Ri, float(L["k"]), float(V["k"]))   # conductivity at each point
q = q0*k0(mu*s)/k0(mu*Rw)                              # gamma source, the same K0 profile z3st uses

Q = cumulative_trapezoid(q*s, s, initial=0.0)
J1 = cumulative_trapezoid(1.0/(k_s*s), s, initial=0.0)
J2 = cumulative_trapezoid(Q/(k_s*s), s, initial=0.0)

# wetted surface:  k dT/dr = H1 (T - T_COOL)    ->  Tw - F/(Rw H1) = T_COOL
# outer surface:  -k dT/dr = U2 (T - T_INF)     ->  U2 Tw + (U2 J1 + 1/Ro) F = Q/Ro + U2 (J2 + T_INF)
A_T = np.array([[1.0, -1.0/(Rw*H1)],
                [U2,  U2*J1[-1] + 1.0/Ro]])
b_T = np.array([T_COOL,
                Q[-1]/Ro + U2*(J2[-1] + T_INF)])
Tw, F = np.linalg.solve(A_T, b_T)

T_s = Tw + F*J1 - J2

# --.. ..- .-.. .-.. --- reference stresses (composite cylinder) --.. ..- .-.. .-.. ---
# In each layer, generalised plane strain (eps_z the same everywhere):
#   u(r) = (1+nu)/(1-nu) alpha I(r)/r + C1 r + C2/r,    I(r) = int dT r dr from the layer inner face
# Five unknowns: C1 and C2 in the liner, C1 and C2 in the vessel, eps_z.

rL, rV = s[s <= Ri], s[s >= Ri]                        # the two layers share the point Ri
dT_L = np.interp(rL, s, T_s) - T_REF
dT_V = np.interp(rV, s, T_s) - T_REF


def layer(m, r, dT, C1, C2, ez):
    """Displacement and the three stresses in one layer, for given C1, C2 and eps_z."""
    E, nu, al = float(m["E"]), float(m["nu"]), float(m["alpha"])
    lam = E*nu/((1 + nu)*(1 - 2*nu))
    G = E/(2*(1 + nu))

    I = cumulative_trapezoid(dT*r, r, initial=0.0)
    kappa = (1 + nu)/(1 - nu)*al

    u = kappa*I/r + C1*r + C2/r
    e_rr = kappa*(dT - I/r**2) + C1 - C2/r**2          # du/dr
    e_tt = u/r
    e_zz = ez
    trace = e_rr + e_tt + e_zz
    thermal = (3*lam + 2*G)*al*dT

    s_rr = lam*trace + 2*G*e_rr - thermal
    s_tt = lam*trace + 2*G*e_tt - thermal
    s_zz = lam*trace + 2*G*e_zz - thermal
    return u, s_rr, s_tt, s_zz


def conditions(x):
    """The five conditions, written as 'left side - right side'; all zero at the solution."""
    C1L, C2L, C1V, C2V, ez = x
    uL, rrL, ttL, zzL = layer(L, rL, dT_L, C1L, C2L, ez)
    uV, rrV, ttV, zzV = layer(V, rV, dT_V, C1V, C2V, ez)
    axial_force = np.trapezoid(zzL*2*np.pi*rL, rL) + np.trapezoid(zzV*2*np.pi*rV, rV)
    return np.array([
        rrL[0] + P,                       # wetted surface: sigma_rr = -P
        rrV[-1],                          # outer surface: sigma_rr = 0
        uL[-1] - uV[0],                   # interface: same displacement
        rrL[-1] - rrV[0],                 # interface: same radial stress
        axial_force - P*np.pi*Rw**2,      # closed end: axial force = P pi Rw^2
    ])


# The conditions are linear in the five unknowns: build the matrix one column at a time,
# switching on one unknown at a time, then solve.
c0 = conditions(np.zeros(5))
A_u = np.column_stack([conditions(np.eye(5)[j]) - c0 for j in range(5)])
x = np.linalg.solve(A_u, -c0)

C1L, C2L, C1V, C2V, ez = x
_, rrL, ttL, zzL = layer(L, rL, dT_L, C1L, C2L, ez)
_, rrV, ttV, zzV = layer(V, rV, dT_V, C1V, C2V, ez)
ref = {"L": (rL, rrL, ttL, zzL), "V": (rV, rrV, ttV, zzV)}


def ref_at(r, comp):
    lay = "L" if r < Ri else "V"
    rr, *sig = ref[lay]
    return np.interp(r, rr, sig[comp])


# --.. ..- .-.. .-.. --- FE solution --.. ..- .-.. .-.. ---
if not os.path.exists(VTU_FILE):
    raise SystemExit(f"[FAIL] no result to check: {VTU_FILE}\n       run ./Allrun first.")
grid = pv.read(VTU_FILE)
line = grid.sample_over_line((Rw, Lz/2, 0.0), (Ro, Lz/2, 0.0), resolution=1040)
T_all = np.asarray(line["Temperature"])
ok = np.asarray(line["vtkValidPointMask"]).astype(bool) & (T_all > 1.0)
r, T_fe, S_fe = line.points[ok, 0], T_all[ok], np.asarray(line["Stress (points)"])[ok]
o = np.argsort(r); r, T_fe, S_fe = r[o], T_fe[o], S_fe[o]
print(f"[INFO] {ok.sum()} of {len(ok)} probe points inside the mesh")

# away from the interface (+-1.5 mm, where a profile blends the two materials) and from the two faces (0.5 mm)
far = (np.abs(r - Ri) > 1.5e-3) & (r > Rw + 5e-4) & (r < Ro - 5e-4)


def L2(num, refv):
    return float(np.sqrt(np.mean((num - refv)**2))/np.sqrt(np.mean(refv**2)))


tt_ref = np.array([ref_at(ri, 1) for ri in r])
rr_ref = np.array([ref_at(ri, 0) for ri in r])
zz_ref = np.array([ref_at(ri, 2) for ri in r])

# the vessel inner surface: the VESSEL cell whose side lies on Ri, at mid-height
cid = grid.find_closest_cell((Ri + 2.5e-4, Lz/2, 0.0))
c_r = grid.cell_centers().points[cid, 0]
assert c_r > Ri, "the probe picked a liner cell"
stt_cell = float(np.asarray(grid["Stress (cells)"])[cid, I_TT])
stt_cell_ref = ref_at(c_r, 1)

print(f"\n  sigma_tt at the vessel inner surface (vessel cell, r = {c_r*1e3:.2f} mm):"
      f" z3st {stt_cell/1e6:8.2f}   reference {stt_cell_ref/1e6:8.2f} MPa")
print(f"  sigma_tt at the vessel inner surface, exactly at Ri (reference): {ref_at(Ri + 1e-12, 1)/1e6:8.2f} MPa")
print(f"  sigma_tt at the wetted surface (liner, reference): {ref['L'][2][0]/1e6:8.2f} MPa")

# --.. ..- .-.. .-.. --- plot --.. ..- .-.. .-.. ---
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
ax[0].plot((s - Ri)*1e3, T_s - 273.15, color="tab:red", lw=2, label="reference")
ax[0].plot((r[::15] - Ri)*1e3, T_fe[::15] - 273.15, "o", ms=4, color="tab:blue", label="z3st")
ax[0].set_ylabel("T (°C)")
for (lay, c) in (("L", "0.4"), ("V", None)):
    rr_, srr, stt, szz = ref[lay]
    for comp, col, lab in ((srr, "tab:blue", r"$\sigma_{rr}$"), (stt, "tab:red", r"$\sigma_{\theta\theta}$"),
                           (szz, "tab:green", r"$\sigma_{zz}$")):
        ax[1].plot((rr_ - Ri)*1e3, comp/1e6, color=col, lw=2, label=lab if lay == "V" else None)
for i, col in ((I_RR, "tab:blue"), (I_TT, "tab:red"), (I_ZZ, "tab:green")):
    ax[1].plot((r[far][::15] - Ri)*1e3, S_fe[far][::15, i]/1e6, "o", ms=3, color=col, alpha=0.7)
ax[1].set_ylabel("stress (MPa)"); ax[1].axhline(0, color="k", lw=0.6)
for a in ax:
    a.axvspan((Rw - Ri)*1e3, 0, color="0.85"); a.set_xlabel("r - Ri (mm)"); a.grid(alpha=0.35); a.legend(fontsize=9)
fig.suptitle("lined gamma-heated cylinder: lines = reference, markers = z3st (liner shaded)")
fig.tight_layout()
fig.savefig(os.path.join(CASE_DIR, "output", "verification.png"), dpi=200)

# --.. ..- .-.. .-.. --- metrics --.. ..- .-.. .-.. ---
def entry(num, refv):
    return {"numerical": float(num), "reference": float(refv),
            "abs_error": float(abs(num - refv)), "rel_error": float(abs(num - refv)/abs(refv))}


rise = T_fe - T_COOL
e_T = L2(rise, np.interp(r, s, T_s) - T_COOL)
errors = {
    "L2_error_temperature": {"numerical": e_T, "reference": 0.0, "abs_error": e_T, "rel_error": e_T},
    "L2_error_sigma_tt": {"numerical": L2(S_fe[far, I_TT], tt_ref[far]), "reference": 0.0,
                          "abs_error": L2(S_fe[far, I_TT], tt_ref[far]), "rel_error": L2(S_fe[far, I_TT], tt_ref[far])},
    "L2_error_sigma_zz": {"numerical": L2(S_fe[far, I_ZZ], zz_ref[far]), "reference": 0.0,
                          "abs_error": L2(S_fe[far, I_ZZ], zz_ref[far]), "rel_error": L2(S_fe[far, I_ZZ], zz_ref[far])},
    "sigma_tt_vessel_inner_surface": entry(stt_cell, stt_cell_ref),
}
pass_fail_check(errors, TOLERANCE, OUT_JSON, CASE_DIR)
regression_check(errors, CASE_DIR)
print("\n[INFO] Non-regression completed.\n")
