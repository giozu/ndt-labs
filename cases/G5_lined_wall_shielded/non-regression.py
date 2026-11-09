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
from scipy.special import k0

from z3st.utils.utils_verification import pass_fail_check, regression_check

import pyvista as pv

CASE_DIR = os.path.dirname(os.path.abspath(__file__))
VTU_FILE = os.path.join(CASE_DIR, "output", "fields.vtu")
OUT_JSON = os.path.join(CASE_DIR, "output", "non-regression.json")


def _yaml(name):
    with open(os.path.join(CASE_DIR, name)) as f:
        return yaml.safe_load(f)


geom = _yaml("geometry.yaml")
Rw, Ri, Ro, Lz = (float(geom[k]) for k in ("inner_radius", "interface_radius", "outer_radius", "Lz"))
mats = {n: _yaml(p) for n, p in _yaml("input.yaml")["materials"].items()}
L, V = mats["liner"], mats["steel"]
mu, q0 = float(V["mu_gamma"]), float(V["gamma_heating"])
assert float(L["mu_gamma"]) == mu and float(L["gamma_heating"]) == q0
assert float(L["T_ref"]) == float(V["T_ref"]), "one stress-free temperature for both layers"
T_REF = float(V["T_ref"])

bcs = _yaml("boundary_conditions.yaml")
_in = bcs["thermal"]["liner"][0]
_out = bcs["thermal"]["steel"][0] if "steel" in bcs["thermal"] else {}   # no condition on the outer face: adiabatic, U2 = 0
H1, T_COOL = float(_in["h_conv"]), float(_in["T_ext"])
U2, T_INF = float(_out.get("h_conv", 0.0)), float(_out.get("T_ext", 0.0))
mech = {bc["region"]: bc for bc in bcs["mechanical"]["steel"] if bc["type"] == "Neumann"}
P = -float(mech["inner_radius"]["traction"])
assert abs(float(mech["top"]["traction"])/(P*Rw**2/(Ro**2 - Rw**2)) - 1) < 1e-5, "top load is not the closed-end one"

TOLERANCE = 1.0e-2
I_RR, I_TT, I_ZZ = 0, 4, 8          # (r, theta, z): 4 is the HOOP component, 8 is axial

# --.. ..- .-.. .-.. --- reference temperature (two layers, K0 source) --.. ..- .-.. .-.. ---
s = np.unique(np.concatenate([np.linspace(Rw, Ri, 4001), np.linspace(Ri, Ro, 40001)]))
kk = np.where(s < Ri, float(L["k"]), float(V["k"]))
q = q0*k0(mu*s)/k0(mu*Rw)


def _int(f):
    return np.concatenate([[0.0], np.cumsum(0.5*(f[1:] + f[:-1])*np.diff(s))])


cum = _int(s*q)
J1, J2 = _int(1.0/(kk*s)), _int(cum/(kk*s))
C = (cum[-1]/Ro - U2*(T_COOL - T_INF - J2[-1]))/(1.0/Ro + U2*(1.0/(Rw*H1) + J1[-1]))
T_s = T_COOL + C/(Rw*H1) + C*J1 - J2

# --.. ..- .-.. .-.. --- reference stresses (composite cylinder) --.. ..- .-.. .-.. ---
def layer(m, mask, r0):
    """Displacement and stresses in one layer as an affine function of (C1, C2, eps_z)."""
    E, nu, al = float(m["E"]), float(m["nu"]), float(m["alpha"])
    lam, G = E*nu/((1 + nu)*(1 - 2*nu)), E/(2*(1 + nu))
    r, dT = s[mask], T_s[mask] - T_REF
    I = np.concatenate([[0.0], np.cumsum(0.5*(dT[1:]*r[1:] + dT[:-1]*r[:-1])*np.diff(r))])
    k_ = (1 + nu)/(1 - nu)*al
    up, dup = k_*I/r, k_*(dT - I/r**2)            # particular u and du/dr
    th = (3*lam + 2*G)*al*dT
    # columns: constant part, C1, C2, eps_z
    u = np.stack([up, r, 1/r, 0*r])
    er = np.stack([dup, np.ones_like(r), -1/r**2, 0*r])
    et = u/r
    ez = np.stack([0*r, 0*r, 0*r, np.ones_like(r)])
    tr = er + et + ez
    srr, stt, szz = lam*tr + 2*G*er, lam*tr + 2*G*et, lam*tr + 2*G*ez
    for a in (srr, stt, szz):
        a[0] -= th
    return r, u, srr, stt, szz


mL, mV = s <= Ri, s >= Ri
rL, uL, rrL, ttL, zzL = layer(L, mL, Rw)
rV, uV, rrV, ttV, zzV = layer(V, mV, Ri)


def lift(arr, which):
    """Embed a 4-row layer array into the 6-column unknown space (1, C1L, C2L, C1V, C2V, ez)."""
    out = np.zeros((6, arr.shape[1]))
    out[0] = arr[0]
    out[[1, 2] if which == "L" else [3, 4]] = arr[1:3]
    out[5] = arr[3]
    return out


uL6, rrL6, ttL6, zzL6 = (lift(a, "L") for a in (uL, rrL, ttL, zzL))
uV6, rrV6, ttV6, zzV6 = (lift(a, "V") for a in (uV, rrV, ttV, zzV))


def area_int(f6, r):                          # int f 2 pi r dr, row by row
    return np.trapezoid(f6*2*np.pi*r, r, axis=1)


A = np.array([rrL6[1:, 0], rrV6[1:, -1], uL6[1:, -1] - uV6[1:, 0], rrL6[1:, -1] - rrV6[1:, 0],
              area_int(zzL6, rL)[1:] + area_int(zzV6, rV)[1:]])
b = -np.array([rrL6[0, 0] + P, rrV6[0, -1], uL6[0, -1] - uV6[0, 0], rrL6[0, -1] - rrV6[0, 0],
               area_int(zzL6, rL)[0] + area_int(zzV6, rV)[0] - P*np.pi*Rw**2])
x = np.concatenate([[1.0], np.linalg.solve(A, b)])
ref = {"L": (rL, x @ rrL6, x @ ttL6, x @ zzL6), "V": (rV, x @ rrV6, x @ ttV6, x @ zzV6)}


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
