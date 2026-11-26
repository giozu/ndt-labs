#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# --.. ..- .-.. .-.. --- Z3ST non-regression script --.. ..- .-.. .-.. ---
"""
NDT course case: LINED, gamma-heated cylinder, thermal analysis.

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
Rw = float(geom["inner_radius"])        # wetted surface (liner inner face)
Ri = float(geom["interface_radius"])    # liner-vessel interface
Ro = float(geom["outer_radius"])        # vessel outer surface
Lz = float(geom["Lz"])

bcs = load_yaml(CASE_DIR, "boundary_conditions.yaml")["thermal"]
h1, T_cool = float(bcs["liner"][0]["h_conv"]), float(bcs["liner"][0]["T_ext"])   # wetted surface
U2, T_inf = float(bcs["steel"][0]["h_conv"]), float(bcs["steel"][0]["T_ext"])    # vessel outer surface

# --.. ..- .-.. .-.. --- FE solution, radial profile at mid-height --.. ..- .-.. .-.. ---
# temperature: nodes on y = Lz/2 (in the axisymmetric mesh x = r, y = axial)
r_T, T = line(VTU_FILE, "Temperature", y=Lz/2, z=0.0, tol=1e-6)

m = r_T >= Ri                           # vessel nodes
T_avg = np.trapezoid(T[m]*r_T[m], r_T[m])/np.trapezoid(r_T[m], r_T[m])
i_max = np.argmax(T)

print(f"T wetted surface:        {T[0] - 273.15:.1f} °C")
print(f"T vessel inner surface:  {np.interp(Ri, r_T, T) - 273.15:.1f} °C")
print(f"T vessel outer surface:  {T[-1] - 273.15:.1f} °C")
print(f"T max:                   {T[i_max] - 273.15:.1f} °C at r - Ri = {(r_T[i_max] - Ri)*1e3:.1f} mm")
print(f"average temperature, vessel: {T_avg - 273.15:.1f} °C\n")

# heat leaving each surface, per metre of height: 2 pi r h (T_surface - T_fluid)
print(f"heat through the wetted surface: {2*np.pi*Rw*h1*(T[0] - T_cool):.1f} W/m")
print(f"heat through the outer surface:  {2*np.pi*Ro*U2*(T[-1] - T_inf):.1f} W/m\n")

# --.. ..- .-.. .-.. --- plot --.. ..- .-.. .-.. ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot((r_T - Ri)*1e3, T - 273.15, "-", color="tab:blue", label="T")
ax.hlines(T_avg - 273.15, 0, (Ro - Ri)*1e3, colors="tab:red", linestyles="--",
          label=f"vessel average: {T_avg - 273.15:.1f}°C")
ax.plot((r_T[i_max] - Ri)*1e3, T[i_max] - 273.15, "o", color="tab:red",
        label=f"max: {T[i_max] - 273.15:.1f}°C")
ax.axvspan((Rw - Ri)*1e3, 0, color="0.85")
ax.set_xlabel("r - Ri (mm)"); ax.set_ylabel("T (°C)"); ax.grid(alpha=0.35); ax.legend(fontsize=9)

fig.suptitle("lined gamma-heated cylinder, z3st (liner shaded)")
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "verification.png"), dpi=200)
