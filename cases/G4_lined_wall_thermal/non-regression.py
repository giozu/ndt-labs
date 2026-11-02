#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# --.. ..- .-.. .-.. --- Z3ST non-regression script --.. ..- .-.. .-.. ---
"""
NDT course case: temperature field of a LINED, gamma-heated cylinder (thermal only)
Author: Giovanni Zullo

Liner Rw..Ri and vessel Ri..Ro, the gamma source entering at the wetted surface Rw,
h1 on the wetted surface and U2 on the outer face: the thermal model of item 6 of the
assignment, on neutral numbers (section 6 of the G4 notebook).

Reference: the SAME gamma source z3st uses, q'''(r) = q0 K0(mu r)/K0(mu Rw) in both
layers, integrated radially by quadrature (numerical integration). Steady cylindrical conduction integrates once to
    r k(r) T'(r) = C - cum(r),        cum(r) = int_Rw^r s q(s) ds,
valid across the interface because the flux r k T' is continuous there; the two Robin
conditions fix C and T(Rw). An independent method (quadrature, not finite elements).

Writes output/non-regression.json and output/verification.png
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml
from scipy.special import k0

from z3st.utils.utils_verification import pass_fail_check, regression_check

import pyvista as pv

# --.. ..- .-.. .-.. --- configuration --.. ..- .-.. .-.. ---
CASE_DIR = os.path.dirname(os.path.abspath(__file__))
VTU_FILE = os.path.join(CASE_DIR, "output", "fields.vtu")
OUT_JSON = os.path.join(CASE_DIR, "output", "non-regression.json")


def _yaml(name):
    with open(os.path.join(CASE_DIR, name)) as f:
        return yaml.safe_load(f)

# --.. ..- .-.. .-.. --- read the case data --.. ..- .-.. .-.. ---
# read geometry.yaml
geom = _yaml("geometry.yaml")
Rw, Ri, Ro, Lz = (float(geom[k]) for k in ("inner_radius", "interface_radius", "outer_radius", "Lz"))
# in the next lines, we check the radial temperature profile from Rw to Ro.
# The FE solution is 2-D, in (r, z); the reference is 1-D, in r only. They are compared
# along the radial line at mid-height, z = Lz/2, far from the top and the bottom (below).

# read input.yaml
mats = {n: _yaml(p) for n, p in _yaml("input.yaml")["materials"].items()} # this line reads input.yaml and the two materials yaml files it points to
# mats is a dict of dicts, one card per material, e.g.
#   {"liner": {"k": 16.0, "mu_gamma": 27.0, "gamma_heating": 2.6e6, ...},
#    "steel": {"k": 20.0, "mu_gamma": 27.0, "gamma_heating": 2.6e6, ...}}
# and we can access the properties of each material by name, e.g., mats["liner"]["k"] or mats["steel"]["mu_gamma"]
k_L, k_V = float(mats["liner"]["k"]), float(mats["steel"]["k"])
mu, q0 = float(mats["steel"]["mu_gamma"]), float(mats["steel"]["gamma_heating"])

# The reference uses ONE source for both layers: the same mu, and the same q0 (its value at Rw),
# in the two cards. Stop here if the cards disagree.
assert float(mats["liner"]["mu_gamma"]) == mu and float(mats["liner"]["gamma_heating"]) == q0, \
    "the reference assumes one mu and one q0 at Rw for both layers"

# read boundary_conditions.yaml
# h1, U2 and the two fluid temperatures read from the BCs, so the reference solution is consistent with the FE solution
bcs = _yaml("boundary_conditions.yaml")["thermal"]
_in = bcs["liner"][0]
_out = bcs["steel"][0] if "steel" in bcs else {}   # no condition on the outer face: adiabatic, U2 = 0 (T_inf is then irrelevant)
H1, T_COOL = float(_in["h_conv"]), float(_in["T_ext"])
U2, T_INF = float(_out.get("h_conv", 0.0)), float(_out.get("T_ext", 0.0))

TOLERANCE = 1.0e-2   # relative, on temperature RISES above the coolant (not on kelvin)

# --.. ..- .-.. .-.. --- analytic reference --.. ..- .-.. .-.. ---
# radial grid, fine, with Ri (the interface) as a node
_s = np.unique(np.concatenate([np.linspace(Rw, Ri, 4001), np.linspace(Ri, Ro, 40001)]))
# conductivity: liner below Ri, vessel above
_k = np.where(_s < Ri, k_L, k_V)
# the gamma source q'''(r) = q0 K0(mu r)/K0(mu Rw), as in z3st
_q = q0*k0(mu*_s)/k0(mu*Rw)
# cum(r) = int_Rw^r s q(s) ds: the heat generated between Rw and r (per radian, per metre)
_cum = np.concatenate([[0.0], np.cumsum(0.5*(_s[1:]*_q[1:] + _s[:-1]*_q[:-1])*np.diff(_s))])


def _int(f):
    """Running trapezoid from Rw. k jumps at Ri, which is a grid node: 1/k is taken as the
    average of the two sides only on the one interval that touches it, a 1e-5 error."""
    return np.concatenate([[0.0], np.cumsum(0.5*(f[1:] + f[:-1])*np.diff(_s))])


J1 = _int(1.0/(_k*_s))          # int 1/(k s)
J2 = _int(_cum/(_k*_s))         # int cum/(k s)
# C = Rw k T'(Rw): the heat leaving through the wetted surface, per radian and per metre,
# so q_inner below is 2 pi C
# inner Robin:  k T'(Rw) = h1 (T(Rw) - T_cool)  ->  T(Rw) = T_cool + C/(Rw h1)
# outer Robin: -k T'(Ro) = U2 (T(Ro) - T_inf),  T(Ro) = T(Rw) + C J1(Ro) - J2(Ro)
C = ((_cum[-1]/Ro - U2*(T_COOL - T_INF - J2[-1]))
     / (1.0/Ro + U2*(1.0/(Rw*H1) + J1[-1])))
T_ref_profile = T_COOL + C/(Rw*H1) + C*J1 - J2


def T_profile(r):
    return np.interp(r, _s, T_ref_profile)


def vessel_average(r, T):
    """Volume-weighted average over the VESSEL only, int T r dr / int r dr on Ri..Ro:
    the quantity the design temperature is defined on (item 8)."""
    m = r >= Ri
    return np.trapezoid(T[m]*r[m], r[m])/np.trapezoid(r[m], r[m])


gen = 2.0*np.pi*_cum[-1]                                   # W per metre of height
q_inner = 2.0*np.pi*Rw*H1*(T_ref_profile[0] - T_COOL)
q_outer = 2.0*np.pi*Ro*U2*(T_ref_profile[-1] - T_INF)

# --.. ..- .-.. .-.. --- extract the finite element (FE) solution --.. ..- .-.. .-.. ---
if not os.path.exists(VTU_FILE):
    raise SystemExit(f"[FAIL] no result to check: {VTU_FILE}\n       run ./Allrun first.")

grid = pv.read(VTU_FILE) # the grid is a pyvista.UnstructuredGrid object, which has points, cells, and point_data (the fields)
line = grid.sample_over_line((Rw, Lz/2.0, 0.0), (Ro, Lz/2.0, 0.0), resolution=1040) # we sample the grid along a line from (Rw, Lz/2, 0) to (Ro, Lz/2, 0) with 1040 points
T_all = np.asarray(line["Temperature"])
# sample_over_line returns ZEROS outside the mesh: drop them before any integral
ok = np.asarray(line["vtkValidPointMask"]).astype(bool) & (T_all > 1.0)
r, T_fe = line.points[ok, 0], T_all[ok]
o = np.argsort(r)
r, T_fe = r[o], T_fe[o]
print(f"[INFO] {ok.sum()} of {len(ok)} probe points inside the mesh")
T_ana = T_profile(r)

# --.. ..- .-.. .-.. --- the numbers item 6 asks for --.. ..- .-.. .-.. ---
def report(Tf):
    i = int(np.argmax(Tf))
    return {"wetted surface": Tf[0], "vessel inner surface": np.interp(Ri, r, Tf),
            "vessel outer surface": Tf[-1], "maximum": Tf[i], "max at r - Ri (mm)": (r[i] - Ri)*1e3,
            "vessel average": vessel_average(r, Tf)}


fe, an = report(T_fe), report(T_ana)
print(f"\n  {'':28}{'z3st':>10}{'reference':>11}")
for key in fe:
    unit = "" if "mm" in key else "  K"
    print(f"  {key:28}{fe[key]:10.2f}{an[key]:11.2f}{unit}")
print("\n  where the gamma heat goes (reference, per metre of height):")
print(f"    generated       {gen:10.1f} W/m")
_pct = lambda q: f"   ({100*q/gen:5.2f} %)" if gen > 0 else ""   # no source: no share to give
print(f"    wetted surface  {q_inner:10.1f} W/m{_pct(q_inner)}")
print(f"    outer surface   {q_outer:10.1f} W/m{_pct(q_outer)}")

# --.. ..- .-.. .-.. --- plot --.. ..- .-.. .-.. ---
x = (r - Ri)*1e3
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, T_ana - 273.15, "-", lw=2, color="tab:red", label="reference (K0 quadrature)")
ax.plot(x[::15], T_fe[::15] - 273.15, "o", ms=5, color="tab:blue", alpha=0.8, label="z3st")
ax.axvspan((Rw - Ri)*1e3, 0.0, color="0.85", label="liner")
ax.set_xlabel("r - Ri  (mm)   (0 = vessel inner surface)")
ax.set_ylabel("temperature (°C)")
ax.set_title(f"Lined wall: vessel average {fe['vessel average'] - 273.15:.1f} °C")
ax.grid(alpha=0.35); ax.legend(fontsize=9)
fig.tight_layout()
plot_path = os.path.join(CASE_DIR, "output", "verification.png")
fig.savefig(plot_path, dpi=200)
print(f"[INFO] Plot saved in: {plot_path}")

# --.. ..- .-.. .-.. --- non-regression metrics --.. ..- .-.. .-.. ---
def entry(num, ref):
    """Compared as rises above the coolant: a 1 % error on 560 K would hide 5 K."""
    num, ref = num - T_COOL, ref - T_COOL
    return {"numerical": float(num), "reference": float(ref),
            "abs_error": float(abs(num - ref)), "rel_error": float(abs(num - ref)/abs(ref))}


rise_f, rise_a = T_fe - T_COOL, T_ana - T_COOL
e_T = float(np.sqrt(np.mean((rise_f - rise_a)**2))/np.sqrt(np.mean(rise_a**2)))
errors = {
    "L2_error_temperature": {"numerical": e_T, "reference": 0.0, "abs_error": e_T, "rel_error": e_T},
    "T_wetted_surface": entry(fe["wetted surface"], an["wetted surface"]),
    "T_vessel_inner_surface": entry(fe["vessel inner surface"], an["vessel inner surface"]),
    "T_max": entry(fe["maximum"], an["maximum"]),
    "T_vessel_average": entry(fe["vessel average"], an["vessel average"]),
}
pass_fail_check(errors, TOLERANCE, OUT_JSON, CASE_DIR)
regression_check(errors, CASE_DIR)

print("\n[INFO] Non-regression completed.\n")
