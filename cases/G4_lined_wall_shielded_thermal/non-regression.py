#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# --.. ..- .-.. .-.. --- Z3ST non-regression script --.. ..- .-.. .-.. ---
"""
NDT course case: temperature field of a SHIELDED, lined, gamma-heated cylinder (thermal only)
Author: Giovanni Zullo

The case G4_lined_wall_thermal with a thermal shield Rs..Rso in the downcomer. The coolant
between shield and liner is not meshed: it enters as convection on the three wetted faces.
The shield takes the full gamma source q0 at its inner face; liner and vessel take
q0 exp(-mu t_s) at the wetted surface Rw.

No reference solution here: the method is checked against the K0 quadrature on the case
without the shield (G4_lined_wall_thermal/non-regression.py), and this case adds no new
physics to it. This script reads the temperatures of the shield and of the vessel, and
compares them with the unshielded wall, if that case has been solved.

Writes output/verification.png
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

import pyvista as pv

# --.. ..- .-.. .-.. --- configuration --.. ..- .-.. .-.. ---
CASE_DIR = os.path.dirname(os.path.abspath(__file__))
VTU_FILE = os.path.join(CASE_DIR, "output", "fields.vtu")
VTU_BARE = os.path.join(CASE_DIR, "..", "G4_lined_wall_thermal", "output", "fields.vtu")   # the same wall, no shield


def _yaml(name):
    with open(os.path.join(CASE_DIR, name)) as f:
        return yaml.safe_load(f)

# --.. ..- .-.. .-.. --- read the case data --.. ..- .-.. .-.. ---
# read geometry.yaml
geom = _yaml("geometry.yaml")
Rs, Rso, Rw, Ri, Ro, Lz = (float(geom[k]) for k in ("inner_radius", "shield_outer_radius", "wetted_radius",
                                                    "interface_radius", "outer_radius", "Lz"))
# in the next lines, we read the radial temperature profile of the shield (Rs to Rso) and of
# the wall (Rw to Ro), along the radial line at mid-height, z = Lz/2, far from the top and the bottom.

# read input.yaml
mats = {n: _yaml(p) for n, p in _yaml("input.yaml")["materials"].items()} # this line reads input.yaml and the three materials yaml files it points to
# mats is a dict of dicts, one card per material, e.g.
#   {"shield": {"k": 20.0, "mu_gamma": 27.0, "gamma_heating": 2.6e6,   "gamma_inner_radius": 0.260, ...},
#    "liner":  {"k": 16.0, "mu_gamma": 27.0, "gamma_heating": 1.734e6, "gamma_inner_radius": 0.296, ...},
#    "steel":  {"k": 20.0, "mu_gamma": 27.0, "gamma_heating": 1.734e6, "gamma_inner_radius": 0.296, ...}}
# and we can access the properties of each material by name, e.g., mats["shield"]["mu_gamma"] or mats["steel"]["gamma_heating"]
mu, q0 = float(mats["shield"]["mu_gamma"]), float(mats["shield"]["gamma_heating"])
q_w = float(mats["steel"]["gamma_heating"])

# z3st does NOT attenuate from one body to the next: the wall (liner+vessel) source is written by hand in the
# liner and steel cards, and must be the shield one attenuated by the shield, q0 exp(-mu t_s).
# A warning is printed if the wall source is not consistent with the shield one.
q_expected = q0*np.exp(-mu*(Rso - Rs))
if abs(q_w/q_expected - 1.0) > 1e-3:
    print(f"[WARNING] wall source {q_w:.4e} W/m3, but the shield passes on q0 exp(-mu t_s) = {q_expected:.4e} W/m3")

# --.. ..- .-.. .-.. --- extract the finite element (FE) solution --.. ..- .-.. .-.. ---
if not os.path.exists(VTU_FILE):
    raise SystemExit(f"[FAIL] no result to read: {VTU_FILE}\n       run ./Allrun first.")


def probe(vtu, a, b, n):
    """T along the radial line a..b at mid-height (Lz/2), sorted by r."""
    grid = pv.read(vtu) # a pyvista.UnstructuredGrid: points, cells, and point_data (the fields)
    line = grid.sample_over_line((a, Lz/2.0, 0.0), (b, Lz/2.0, 0.0), resolution=n) # n points from (a, Lz/2, 0) to (b, Lz/2, 0)
    T_all = np.asarray(line["Temperature"])
    # sample_over_line returns ZEROS outside the mesh: drop them before any integral
    ok = np.asarray(line["vtkValidPointMask"]).astype(bool) & (T_all > 1.0)
    r, T = line.points[ok, 0], T_all[ok]
    o = np.argsort(r)
    return r[o], T[o]


r_sh, T_sh = probe(VTU_FILE, Rs, Rso, 300)     # the shield
r, T_fe = probe(VTU_FILE, Rw, Ro, 1040)        # liner + vessel
print(f"[INFO] {len(r_sh)} probe points in the shield, {len(r)} in liner + vessel")
bare = os.path.exists(VTU_BARE)
if bare:
    r_b, T_b = probe(VTU_BARE, Rw, Ro, 1040)   # liner + vessel, no shield


# support function, to compute the average temperature in
# cylindrical coordinates
def average(r, T, a, b):
    """Volume-weighted average on a..b, int T r dr / int r dr: on the vessel (Ri..Ro) it is
    the quantity the design temperature is defined on (item 8)."""
    m = (r >= a) & (r <= b)
    return np.trapezoid(T[m]*r[m], r[m])/np.trapezoid(r[m], r[m])

# --.. ..- .-.. .-.. --- the numbers items 4 and 8 ask for --.. ..- .-.. .-.. ---
def report_shield(r, T):
    i = int(np.argmax(T))
    return {"inner face": T[0], "outer face": T[-1], "maximum": T[i],
            "max at r - Rs (mm)": (r[i] - Rs)*1e3, "average": average(r, T, Rs, Rso)}


def report(r, T):
    i = int(np.argmax(T))
    return {"wetted surface": T[0], "vessel inner surface": np.interp(Ri, r, T),
            "vessel outer surface": T[-1], "maximum": T[i], "max at r - Ri (mm)": (r[i] - Ri)*1e3,
            "vessel average": average(r, T, Ri, Ro)}


sh = report_shield(r_sh, T_sh)
fe = report(r, T_fe)
nb = report(r_b, T_b) if bare else None

print(f"\n  {'THERMAL SHIELD':28}{'z3st':>10}")
for key in sh:
    unit = "" if "mm" in key else "  K"
    print(f"  {key:28}{sh[key]:10.2f}{unit}")

print(f"\n  {'LINER + VESSEL':28}{'shield':>10}{'no shield':>11}")
for key in fe:
    unit = "" if "mm" in key else "  K"
    other = f"{nb[key]:11.2f}" if bare else f"{'-':>11}"
    print(f"  {key:28}{fe[key]:10.2f}{other}{unit}")
if bare:
    print(f"\n  the shield lowers the vessel average by {nb['vessel average'] - fe['vessel average']:.1f} K")
else:
    print(f"\n[INFO] {VTU_BARE} not found: run G4_lined_wall_thermal/Allrun to compare with the unshielded wall")

# --.. ..- .-.. .-.. --- plot --.. ..- .-.. .-.. ---
x, x_sh = (r - Ri)*1e3, (r_sh - Ri)*1e3
fig, ax = plt.subplots(figsize=(9, 5))

# Temperature profile: FE solution (z3st), with the shield and, if solved, without it
if bare:
    ax.plot((r_b - Ri)*1e3, T_b - 273.15, "--", lw=2, color="0.5", label="no shield (G4_lined_wall_thermal)")
ax.plot(x, T_fe - 273.15, "-", lw=2, color="tab:blue", label="z3st, with the shield")
ax.plot(x_sh, T_sh - 273.15, "-", lw=2, color="tab:blue")

# Horizontal lines, the average temperature of the shield and the mean metal temperature of the vessel
ax.hlines(sh["average"] - 273.15, (Rs - Ri)*1e3, (Rso - Ri)*1e3, colors='tab:green', linestyles='--',
          label=f'shield average: {sh["average"] - 273.15:.1f}°C')
avg = fe["vessel average"]
ax.hlines(avg - 273.15, 0, (Ro - Ri)*1e3, colors='tab:red', linestyles='--',
          label=f'mean metal temperature (NCA-2142.1(b)): {avg - 273.15:.1f}°C')

# Maximum temperature of the vessel, and its position from the vessel inner surface
x_max, T_max = fe["max at r - Ri (mm)"], fe["maximum"]
ax.plot(x_max, T_max - 273.15, 'o', ms=9, color='tab:red',
        label=f'vessel maximum: {T_max - 273.15:.1f}°C at {x_max:.1f} mm')

# Horizontal line, the temperature limit of the vessel steel (NB-1120, NB-3112.4)
# >>> CHANGE HERE: 400 degC is the limit of the NEUTRAL steel of this case
T_lim = 400.0   # degC
ax.hlines(T_lim, 0, (Ro - Ri)*1e3, colors='k', linestyles='-.', label=f'temperature limit of the vessel steel: {T_lim:.0f}°C')

# Mark the shield, the coolant channel and the liner with shaded areas
ax.axvspan((Rs - Ri)*1e3, (Rso - Ri)*1e3, color="tab:green", alpha=0.12, label="shield")
ax.axvspan((Rso - Ri)*1e3, (Rw - Ri)*1e3, color="tab:cyan", alpha=0.12, label="coolant (not meshed)")
ax.axvspan((Rw - Ri)*1e3, 0.0, color="0.85", label="liner")

# x-y labels, title, grid, legend
ax.set_xlabel("r - Ri  (mm)   (0 = vessel inner surface)")
ax.set_ylabel("temperature (°C)")
ax.set_title(f"Shielded lined wall: vessel average {avg - 273.15:.1f} °C")
ax.grid(alpha=0.35); ax.legend(fontsize=8)
fig.tight_layout()

plot_path = os.path.join(CASE_DIR, "output", "verification.png")
fig.savefig(plot_path, dpi=200)
print(f"[INFO] Plot saved in: {plot_path}")

print("\n[INFO] Non-regression completed.\n")
