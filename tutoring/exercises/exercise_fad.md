# Exercise: brittle fracture and the Fracture Analysis Diagram

A ferritic steel for a pressure vessel. Its stress-temperature diagram for crack initiation
and arrest is below, drawn after Weisman for his carbon steel, whose nil-ductility
temperature NDT, where yield and tensile strength coincide, is -12 °C (10 °F). For another
steel the whole diagram moves with its NDT: use the distances in the table.

![Stress-temperature diagram for crack initiation and arrest](../M2_constitutive/figures/03_fracture_analysis_diagram.png)

| data | value |
|---|---|
| yield strength | $S_y = 300$ MPa |
| tensile strength | $S_u = 480$ MPa |
| lower fracture propagation stress | about 45 MPa (6500 psi) |
| NDT with a small flaw | NDT + 28 °C (50 °F) |
| FTE, crack-arrest curve at $S_y$ | NDT + 33 °C (60 °F) |
| FTP, crack-arrest curve at $S_u$ | just above FTE |

Temperature differences in °F convert with the factor 5/9 alone; absolute temperatures with
$(T_F - 32)\cdot 5/9$.

## Questions

1. A crack is already running through the steel. Does it keep running or is it arrested in each case?
   (a) NDT - 10 °C, 30 MPa; (b) NDT - 10 °C, 150 MPa; (c) NDT + 45 °C, 250 MPa;
   (d) NDT + 20 °C, 300 MPa; (e) NDT + 60 °C, 400 MPa.
2. The stress on the vertical axis is the applied stress **plus the residual stress**. A welded vessel is
   loaded to a membrane stress of 100 MPa, a third of $S_y$. Why does it still have to be
   pressurised above FTE?
3. A vessel is brought to pressure at no less than 4 °C (40 °F), and its total stress
   reaches $S_y$. What is the highest NDT the steel may have? What is the most stress the
   vessel may carry below that NDT?
4. The steel is bought with NDT = -30 °C (-22 °F). After years of service, surveillance
   specimens show an NDT shift of 50 °C (90 °F).
   (a) Where are NDT, the NDT with a small flaw, and FTE now?
   (b) May the vessel still be brought to full pressure at 4 °C?
   (c) What is the lowest temperature at which it may?
5. Why does irradiation move NDT to the right? Answer with the Davidenkov construction:
   the yield stress against the cleavage fracture stress.

---

## Solution

### 1. Reading the diagram

The crack-arrest curve D runs along the lower fracture propagation stress, about 45 MPa,
then rises steeply. It crosses the yield curve at FTE = NDT + 33 °C, and reaches the tensile
strength at FTP just after.

| case | where | verdict |
|:---|:---|:---|
| (a) NDT - 10 °C, 30 MPa | under the lower fracture propagation stress | **arrested**: below about 45 MPa no crack runs, at any temperature |
| (b) NDT - 10 °C, 150 MPa | above it, left of curve D | **propagates** |
| (c) NDT + 45 °C, 250 MPa | right of FTE, below $S_y$ | **arrested**: past FTE no crack runs under elastic stress |
| (d) NDT + 20 °C, 300 MPa | at yield, left of FTE | **propagates**: FTE is NDT + 33 °C |
| (e) NDT + 60 °C, 400 MPa | right of FTP, above yield | no brittle fracture: past FTP failure is by shear |

Cases (c) and (d) carry nearly the same stress and differ only in temperature. That is the
point of the diagram: whether a stress is safe depends on how far above NDT the steel is.

### 2. Residual stress

A weld leaves residual stresses that stress relief does not remove entirely. The amount
left can conservatively be taken as of the order of the yield strength (Harvey, 1974,
§5.22). The total, applied plus residual, then reaches $S_y$ even though the applied load is
only a third of it. A crack can run at $S_y$ anywhere left of FTE, so the vessel has to be above FTE before
it is pressurised.

### 3. Choosing a steel

At $S_y$ the vessel has to be at or above FTE when it is pressurised:

```math
\text{NDT} + 33\ ^\circ\text{C} \le 4\ ^\circ\text{C}
\quad\Rightarrow\quad
\text{NDT} \le -29\ ^\circ\text{C}\ (-20\ ^\circ\text{F})
```

In °F the data are round: 40 - 60 = -20 °F = -28.9 °C.

Below NDT the total stress must stay under the lower fracture propagation stress, **about
45 MPa (6500 psi)**. On a cold vessel that is a small fraction of the operating stress
(Weisman, 1977, §10.4).

### 4. A vessel ages

(a) Every temperature on the diagram is counted from NDT, so the whole diagram moves by the
shift:

| | as bought | after the shift |
|:---|:---:|:---:|
| NDT | -30 °C (-22 °F) | **20 °C (68 °F)** |
| NDT with a small flaw = NDT + 28 °C | -2 °C (28 °F) | **48 °C (118 °F)** |
| FTE = NDT + 33 °C | 3 °C (38 °F) | **53 °C (128 °F)** |

(b) **No.** At 4 °C the steel is now 16 °C *below* its NDT: only the lower fracture
propagation stress, about 45 MPa, is allowed. When new, 4 °C was just above FTE and the
vessel could be loaded to yield.

(c) Full pressure needs $T \ge$ FTE: **53 °C (128 °F)**. The vessel has to be heated before it
is pressurised, and the minimum pressurisation temperature has risen by the whole shift,
50 °C.

### 5. Why irradiation moves NDT

Neutrons fill the lattice with defects that obstruct dislocations. The yield stress rises
at every temperature, while the cleavage fracture stress hardly changes. The temperature
where the two cross, below which the steel cleaves before it can yield, moves up. So does
NDT, and with it the whole diagram.
