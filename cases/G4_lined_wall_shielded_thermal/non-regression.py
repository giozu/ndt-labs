#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# --.. ..- .-.. .-.. --- Z3ST non-regression script --.. ..- .-.. .-.. ---
"""
NDT course case: SHIELDED, lined, gamma-heated cylinder, thermal analysis.

Author: Giovanni Zullo
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import numpy as np

from z3st.utils.non_regression import case_paths, line, load_yaml

CASE_DIR, VTU_FILE, OUT_JSON = case_paths(__file__)
OUT_DIR = os.path.dirname(OUT_JSON)

# --.. ..- .-.. .-.. --- case data --.. ..- .-.. .-.. ---
geom = load_yaml(CASE_DIR, "geometry.yaml")
Rs = float(geom["inner_radius"])          # shield inner face
Rso = float(geom["shield_outer_radius"])  # shield outer face
Rw = float(geom["wetted_radius"])         # wetted surface (liner inner face)
Ri = float(geom["interface_radius"])      # liner-vessel interface
Ro = float(geom["outer_radius"])          # vessel outer surface
Lz = float(geom["Lz"])

# --.. ..- .-.. .-.. --- FE solution, radial profile at mid-height --.. ..- .-.. .-.. ---
# temperature: nodes on y = Lz/2 (in the axisymmetric mesh x = r, y = axial)
r_T, T = line(VTU_FILE, "Temperature", y=Lz/2, z=0.0, tol=1e-6)

# the coolant between shield and liner is not meshed: two separate bodies
s = r_T <= Rso                          # shield nodes
w = r_T >= Rw                           # liner + vessel nodes
m = r_T >= Ri                           # vessel nodes

T_avg_s = np.trapezoid(T[s]*r_T[s], r_T[s])/np.trapezoid(r_T[s], r_T[s])
T_avg_v = np.trapezoid(T[m]*r_T[m], r_T[m])/np.trapezoid(r_T[m], r_T[m])

print(f"T max, shield:           {T[s].max() - 273.15:.1f} °C")
print(f"average temperature, shield: {T_avg_s - 273.15:.1f} °C\n")

print(f"T wetted surface:        {T[w][0] - 273.15:.1f} °C")
print(f"T max, vessel:           {T[m].max() - 273.15:.1f} °C")
print(f"average temperature, vessel: {T_avg_v - 273.15:.1f} °C\n")

# --.. ..- .-.. .-.. --- plot --.. ..- .-.. .-.. ---
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot((r_T[s] - Ri)*1e3, T[s] - 273.15, "-", color="tab:green", label="shield")
ax.plot((r_T[w] - Ri)*1e3, T[w] - 273.15, "-", color="tab:blue", label="liner + vessel")
ax.hlines(T_avg_v - 273.15, 0, (Ro - Ri)*1e3, colors="tab:red", linestyles="--",
          label=f"vessel average: {T_avg_v - 273.15:.1f}°C")
ax.axvspan((Rso - Ri)*1e3, (Rw - Ri)*1e3, color="tab:cyan", alpha=0.12, label="coolant (not meshed)")
ax.axvspan((Rw - Ri)*1e3, 0, color="0.85")
ax.set_xlabel("r - Ri (mm)"); ax.set_ylabel("T (°C)"); ax.grid(alpha=0.35); ax.legend(fontsize=9)

fig.suptitle("shielded lined gamma-heated cylinder, z3st (liner shaded)")
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "verification.png"), dpi=200)
