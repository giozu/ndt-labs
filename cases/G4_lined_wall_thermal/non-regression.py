#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# --.. ..- .-.. .-.. --- Z3ST non-regression script --.. ..- .-.. .-.. ---
"""
NDT course case: temperature field of a LINED, gamma-heated cylinder (thermal only)
Author: Giovanni Zullo

Liner Ri..Rm and vessel Rm..Ro, the gamma source entering at the wetted surface Ri,
h1 on the wetted surface and U2 on the outer face: the thermal model of item 6 of the
assignment, on neutral numbers (section 6 of the G4 notebook).

Reference: the SAME gamma source z3st uses -- q'''(r) = q0 K0(mu r)/K0(mu Ri) in both
layers -- integrated radially by quadrature. Steady cylindrical conduction integrates once to
    r k(r) T'(r) = C - cum(r),        cum(r) = int_Ri^r s q(s) ds,
valid across the interface because the flux r k T' is continuous there; the two Robin
conditions fix C and T(Ri). An independent method (quadrature, not finite elements).

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


geom = _yaml("geometry.yaml")
Ri, Rm, Ro, Lz = (float(geom[k]) for k in ("Ri", "Rm", "Ro", "Lz"))
mats = {n: _yaml(p) for n, p in _yaml("input.yaml")["materials"].items()}
k_L, k_V = float(mats["liner"]["k"]), float(mats["steel"]["k"])
mu, q0 = float(mats["steel"]["mu_gamma"]), float(mats["steel"]["gamma_heating"])
assert float(mats["liner"]["mu_gamma"]) == mu and float(mats["liner"]["gamma_heating"]) == q0, \
    "the reference assumes one mu and one q0 at Ri for both layers"

# h1, U2 and the two fluid temperatures read from the BCs, so the reference cannot drift
bcs = _yaml("boundary_conditions.yaml")["thermal"]
_in, _out = bcs["liner"][0], bcs["steel"][0]
H1, T_COOL = float(_in["h_conv"]), float(_in["T_ext"])
U2, T_INF = float(_out["h_conv"]), float(_out["T_ext"])

TOLERANCE = 1.0e-2   # relative, on temperature RISES above the coolant (not on kelvin)

# --.. ..- .-.. .-.. --- analytic reference --.. ..- .-.. .-.. ---
_s = np.unique(np.concatenate([np.linspace(Ri, Rm, 4001), np.linspace(Rm, Ro, 40001)]))
_k = np.where(_s < Rm, k_L, k_V)
_q = q0*k0(mu*_s)/k0(mu*Ri)
_cum = np.concatenate([[0.0], np.cumsum(0.5*(_s[1:]*_q[1:] + _s[:-1]*_q[:-1])*np.diff(_s))])


def _int(f):
    """Running trapezoid from Ri. k jumps at Rm, which is a grid node: 1/k is taken as the
    average of the two sides only on the one interval that touches it, a 1e-5 error."""
    return np.concatenate([[0.0], np.cumsum(0.5*(f[1:] + f[:-1])*np.diff(_s))])


J1 = _int(1.0/(_k*_s))          # int 1/(k s)
J2 = _int(_cum/(_k*_s))         # int cum/(k s)
# inner Robin:  k T'(Ri) = h1 (T(Ri) - T_cool)  ->  T(Ri) = T_cool + C/(Ri h1)
# outer Robin: -k T'(Ro) = U2 (T(Ro) - T_inf),  T(Ro) = T(Ri) + C J1(Ro) - J2(Ro)
C = ((_cum[-1]/Ro - U2*(T_COOL - T_INF - J2[-1]))
     / (1.0/Ro + U2*(1.0/(Ri*H1) + J1[-1])))
T_ref_profile = T_COOL + C/(Ri*H1) + C*J1 - J2


def T_profile(r):
    return np.interp(r, _s, T_ref_profile)


def vessel_average(r, T):
    """Volume-weighted average over the VESSEL only, int T r dr / int r dr on Rm..Ro:
    the quantity the design temperature is defined on (item 8)."""
    m = r >= Rm
    return np.trapezoid(T[m]*r[m], r[m])/np.trapezoid(r[m], r[m])


gen = 2.0*np.pi*_cum[-1]                                   # W per metre of height
q_inner = 2.0*np.pi*Ri*H1*(T_ref_profile[0] - T_COOL)
q_outer = 2.0*np.pi*Ro*U2*(T_ref_profile[-1] - T_INF)

# --.. ..- .-.. .-.. --- extract the FE solution --.. ..- .-.. .-.. ---
if not os.path.exists(VTU_FILE):
    raise SystemExit(f"[FAIL] no result to check: {VTU_FILE}\n       run ./Allrun first.")

grid = pv.read(VTU_FILE)
line = grid.sample_over_line((Ri, Lz/2.0, 0.0), (Ro, Lz/2.0, 0.0), resolution=1040)
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
    return {"wetted surface": Tf[0], "vessel inner surface": np.interp(Rm, r, Tf),
            "vessel outer surface": Tf[-1], "maximum": Tf[i], "max at r - Rm (mm)": (r[i] - Rm)*1e3,
            "vessel average": vessel_average(r, Tf)}


fe, an = report(T_fe), report(T_ana)
print(f"\n  {'':28}{'z3st':>10}{'reference':>11}")
for key in fe:
    unit = "" if "mm" in key else "  K"
    print(f"  {key:28}{fe[key]:10.2f}{an[key]:11.2f}{unit}")
print("\n  where the gamma heat goes (reference, per metre of height):")
print(f"    generated       {gen:10.1f} W/m")
print(f"    wetted surface  {q_inner:10.1f} W/m   ({100*q_inner/gen:5.2f} %)")
print(f"    outer surface   {q_outer:10.1f} W/m   ({100*q_outer/gen:5.2f} %)")

# --.. ..- .-.. .-.. --- plot --.. ..- .-.. .-.. ---
x = (r - Rm)*1e3
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, T_ana - 273.15, "-", lw=2, color="tab:red", label="reference (K0 quadrature)")
ax.plot(x[::15], T_fe[::15] - 273.15, "o", ms=5, color="tab:blue", alpha=0.8, label="z3st")
ax.axvspan((Ri - Rm)*1e3, 0.0, color="0.85", label="liner")
ax.set_xlabel("r - Rm  (mm)   (0 = vessel inner surface)")
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
