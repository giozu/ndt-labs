# M1 — Continuum mechanics in practice

**Module M1 of the optional pre-course. 2.5 hours.**

`M1_continuum.ipynb` — numpy/matplotlib **plus sympy** (only for the compatibility demo;
sympy ships with Colab and with the z3st environment).

## Contents

1. Traction and the Cauchy tensor; index notation; why σ is symmetric
2. Equilibrium, and why three equations can never determine six unknowns
3. Principal stresses, invariants, and what "invariant" buys you
4. Mohr's circles — **sampled**, not drawn: 20 000 random planes land in the predicted
   region, and τ_max = (σ₁−σ₃)/2 comes out of the samples
5. Hydrostatic / deviatoric split; J₂ and where von Mises comes from
6. Small strain, and what compatibility actually means
7. Six exercises

## Builds towards

Everything. Luzzi opens with ~4 h of continuum-mechanics recalls and moves fast; this is
the operational subset needed to keep up.

## Notes for the TA

- §4 is the section to protect. τ_max = (σ₁−σ₃)/2 **depends only on the largest and
  smallest** principal stresses — the intermediate one is irrelevant. That single fact is
  the Tresca criterion, and therefore the ASME stress intensity. Students who internalise
  it here will not be puzzled by "S.I. = σ₁ − σ₃" in December.
- The Mohr section deliberately samples random planes rather than plotting the closed-form
  circles: the point is that the region is a *consequence*, not a definition.
- §6 sets up the thermal-stress module: "plane sections remain plane" is a
  compatibility condition, and
  that restriction is what generates thermal stress. Compatibility is half the physics,
  not bookkeeping.
- The compatibility cell contrasts a strain field derived from a real displacement
  (residual 0) with an invented one (residual 4).

All 5 code cells were executed and verified on 2026-07-31.
