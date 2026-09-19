# M1 - Fundamentals of continuum mechanics

**Module M1 of the optional tutoring track.**

`M1_continuum.ipynb`: numpy and matplotlib, **plus sympy** for the compatibility demo in
§6. Sympy ships with Colab and with any standard scientific Python. Nothing else is
needed: no install, no bootstrap cell.

## Contents

1. Traction and the Cauchy tensor: the two laws of Cauchy, the tetrahedron, index
   notation, and why σ is symmetric
2. Equilibrium, and why three equations can never determine six unknowns
3. Principal stresses, invariants, and what "invariant" buys you
4. Mohr's circles; τ_max = (σ₁ − σ₃)/2
5. Hydrostatic and deviatoric parts; J₂ and where von Mises comes from
6. Small strain, and what compatibility actually means
7. Saint-Venant's principle, and the one place it fails
8. Six exercises

## What it produces

Executed end to end with zero errors. The numbers it prints, for the record:

| | |
|---|---|
| neutral stress state | σ = [[120, 45, −20], [45, −60, 30], [−20, 30, 80]] MPa |
| principal stresses | 133.89, 84.00, −77.89 MPa |
| invariants | I₁ = 140, I₂ = −5725, I₃ = −876000 |
| τ_max, from 20 000 sampled planes and from (σ₁−σ₃)/2 | 105.89 MPa, both |
| mean normal stress | σ_m = 46.67 MPa, so a pressure of −46.67 MPa |
| von Mises, from J₂ and from the principal stresses | 191.77 MPa, both |
| Tresca, and the ratio to von Mises | 211.79 MPa, 1.1044 (bounded by 2/√3 = 1.1547) |
| stress concentration at a circular hole | K_t = 3.00, at any hole size |

## Background reading

Ye, *Structural and Stress Analysis*: chapter **1** (forces, stress, strain, Hooke),
chapter **7** (two-dimensional stress and Mohr's circle) and **8.1** (strain
transformation). Section 7 of the notebook is his **2.7**. Chapters **4** and **8.2**,
beam diagrams and strain gauges, are reading only.
