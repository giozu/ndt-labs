#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# --.. ..- .-.. .-.. --- Z3ST non-regression script --.. ..- .-.. .-.. ---
"""
NDT course case: LINED, gamma-heated cylinder, thermo-mechanical analysis.

Author: Giovanni Zullo
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import numpy as np
from scipy.special import k0

from z3st.utils.non_regression import case_paths, line, load_yaml

CASE_DIR, VTU_FILE, OUT_JSON = case_paths(__file__)
OUT_DIR = os.path.dirname(OUT_JSON)

# --.. ..- .-.. .-.. --- case data --.. ..- .-.. .-.. ---
geom = load_yaml(CASE_DIR, "geometry.yaml")
Rw = float(geom["inner_radius"])        # wetted surface (liner inner face)
Ri = float(geom["interface_radius"])    # liner-vessel interface
Ro = float(geom["outer_radius"])        # vessel outer surface
Lz = float(geom["Lz"])

materials = load_yaml(CASE_DIR, "input.yaml")["materials"]
L = load_yaml(CASE_DIR, materials["liner"])
V = load_yaml(CASE_DIR, materials["steel"])

# --.. ..- .-.. .-.. --- FE solution, radial profiles at mid-height --.. ..- .-.. .-.. ---
# temperature: nodes on y = Lz/2 (in the axisymmetric mesh x = r, y = axial)
r_T, T = line(VTU_FILE, "Temperature", y=Lz/2, z=0.0, tol=1e-6)

# stress: cell values, one material per cell
# components (r, theta, z): 0 radial, 4 HOOP, 8 axial
r_S, s_rr = line(VTU_FILE, "Stress (cells)", component=0, y=Lz/2, z=0.0, tol=Lz/20)
_,   s_tt = line(VTU_FILE, "Stress (cells)", component=4, y=Lz/2, z=0.0, tol=Lz/20)
_,   s_zz = line(VTU_FILE, "Stress (cells)", component=8, y=Lz/2, z=0.0, tol=Lz/20)

# sigma_theta_theta at the vessel inner radius
stt_vessel = s_tt[r_S > Ri][0]
print(f"sigma_tt at the vessel inner radius: {stt_vessel/1e6:.2f} MPa\n")

# --.. ..- .-.. .-.. --- plots --.. ..- .-.. .-.. ---
# gamma source through liner and vessel

# gamma source in each layer: q'''(r) = q'''0 K0(mu r)/K0(mu R_ref)
# liner
muL = float(L["mu_gamma"])                      # attenuation coefficient (1/m)
qL = float(L["gamma_heating"])                  # q'''0 (W/m3)
RL = float(L.get("gamma_inner_radius", Rw))     # R_ref, where q'''0 is given (m)

# vessel (steel)
muV = float(V["mu_gamma"])
qV = float(V["gamma_heating"])
RV = float(V.get("gamma_inner_radius", Rw))

print(f"q'''0 (W/m3) read from liner_neutral.yaml = {qL:.2f}")
print(f"reference radius (m) read from liner_neutral.yaml = {RL:.3f}\n")

print(f"q'''0 (W/m3) read from steel_neutral.yaml = {qV:.2f}")
print(f"reference radius (m) read from steel_neutral.yaml = {RV:.3f}")

sL = np.linspace(Rw, Ri, 200)     # liner
sV = np.linspace(Ri, Ro, 2000)    # vessel
q_L = qL*k0(muL*sL)/k0(muL*RL)
q_V = qV*k0(muV*sV)/k0(muV*RV)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot((sL - Ri)*1e3, q_L, "-",color="tab:red", label="q'''(r)")
ax.plot((sV - Ri)*1e3, q_V, "-", color="tab:blue")
ax.axvline(0, color="k", lw=0.6)
ax.set_xlabel("r - Ri (mm)"); ax.set_ylabel("q''' (W/m3)")
ax.axvspan((Rw - Ri)*1e3, 0, color="0.85"); ax.grid(alpha=0.35); ax.legend(fontsize=9)

fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "gamma_power.png"), dpi=200)

# temperature and stresses
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
ax[0].plot((r_T - Ri)*1e3, T - 273.15, "-", color="tab:blue", label="T")
ax[0].set_ylabel("T (°C)")

ax[1].plot((r_S - Ri)*1e3, s_rr/1e6, "-", color="tab:blue", label=r"$\sigma_{rr}$")
ax[1].plot((r_S - Ri)*1e3, s_tt/1e6, "-", color="tab:red", label=r"$\sigma_{\theta\theta}$")
ax[1].plot((r_S - Ri)*1e3, s_zz/1e6, "-", color="tab:green", label=r"$\sigma_{zz}$")

ax[1].set_ylabel("stress (MPa)"); ax[1].axhline(0, color="k", lw=0.6)

ax[0].axvspan((Rw - Ri)*1e3, 0, color="0.85"); ax[0].set_xlabel("r - Ri (mm)"); ax[0].grid(alpha=0.35); ax[0].legend(fontsize=9)
ax[1].axvspan((Rw - Ri)*1e3, 0, color="0.85"); ax[1].set_xlabel("r - Ri (mm)"); ax[1].grid(alpha=0.35); ax[1].legend(fontsize=9)

fig.suptitle("lined gamma-heated cylinder, z3st (liner shaded)")
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "verification.png"), dpi=200)

m = r_T >= Ri
T_avg = np.trapezoid(T[m]*r_T[m], r_T[m])/np.trapezoid(r_T[m], r_T[m])
print(f"average temperature, vessel: {T_avg - 273.15:.1f} °C\n")