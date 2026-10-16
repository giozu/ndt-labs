# Exercise: thermal creep assessment with the Larson-Miller parameter (LMP or $P_{LM}$)

A master curve collapses rupture (or strain-rate) data taken at many temperatures onto one curve, $\sigma$ against a time-temperature parameter. 
To answer the questions below, we follow similar steps:

1. fix two of $(\sigma, T, t)$, 
2. read or compute the parameter, 
3. and solve for the third.

The only thing to get right is **which value goes in for the quantity you are not solving for**. 

**Where the parameter comes from.** Creep is thermally activated, so the rupture time follows Arrhenius, with a constant $A$:

$$t_R = A\,e^{Q/RT} \;\Rightarrow\; \log_{10} t_R = \log_{10} A + \frac{Q}{2.303\,R\,T} \qquad (2.303 = \ln 10).$$

$A$ is a very short time: about $10^{-20}$ h for steels, so $\log_{10} A \approx -20$. Larson and
Miller set $C = -\log_{10} A$ so that the constant comes out positive, and the minus sign
has no other meaning. Multiplying by $T$:

$$T\,(C + \log_{10} t_R) = \frac{Q(\sigma)}{2.303\,R} = P_{LM}.$$

The activation energy depends on stress, so **at a given $\sigma$ the parameter is fixed**, and every $(T, t_R)$ pair with that $P_{LM}$ ruptures at that stress. 

On a plot of $\log_{10} t_R$ against $1/T$, each stress is a straight line of slope $Q(\sigma)/(2.303R)$. The Larson-Miller assumption is that all these lines meet at one point, $1/T \to 0$, $\log_{10} t_R = -C$. That is why one parameter is enough: stress changes only the slope, and the slope is $P_{LM}$.

For deformation the rate goes as the inverse of a time (Monkman-Grant relationship, the product of the minimum/secondary creep rate and the time to rupture is approximately constant): $\dot\varepsilon_s = B\,e^{-Q/RT}$,
so the sign of the $Q$ term flips. With $C' = \log_{10} B \approx 10$ (rate in 1/h), the parameter becomes $P'_{LM} = T\,(C' - \log_{10}\dot\varepsilon_s)$.

## 1. First exercise: 24CrMo5 beam

A beam of 24CrMo5 steel works at $T = 550$°C $= 823$ K under $\sigma = 55$ MPa. Expected life $t = 8000$ h, allowable strain $\varepsilon_{max} = 1.5$ %. Find the margins against rupture and against excessive deformation. The master curves of the steel are given, $\sigma$ against $P_{LM}$ ($C = 20$) and against $P'_{LM}$ ($C' = 10$); the readings used below are 85 MPa and $20.2\cdot10^3$ on the first, 105 MPa and $13.7\cdot10^3$ on the second.

A margin $\xi$ is always (limit value)/(actual value) of one quantity, **with the other two held at their design values**.

### 1.1 Rupture, $P_{LM} = T\,(20 + \log_{10} t_R)$, $t$ in h, $T$ in K

| Margin | Hold fixed | Solve for | Result |
|--------|------------|-----|------------------------------|
| stress | $T = 823$ K, $t = 8000$ h | $\sigma_R$ | $P_{LM} = 823\,(20 + 3.90) = 19.67\cdot10^3$ → curve → $\sigma_R = 85$ MPa, $\xi_\sigma = 85/55 = 1.55$ |
| time | $T = 823$ K, $\sigma = 55$ MPa | $t_R$ | curve → $P_{LM} = 20.2\cdot10^3$, $\log_{10} t_R = 20.2\cdot10^3/823 - 20 = 4.54$, $t_R \approx 34\,700$ h, $\xi_t = 4.3$ |
| temperature | $\sigma = 55$ MPa, $t = 8000$ h | $T_R$ | $T_R = 20.2\cdot10^3/(20 + 3.90) = 845$ K, $\Delta T = 22$ K, $\xi_T = 1.03$ |

**22 K of extra temperature eat the whole rupture life**, while the stress margin looks
comfortable at 1.5. Creep is far more sensitive to temperature than to stress.

Look at the temperature row: it holds $t$ at the **required** 8000 h, not at the
predicted $t_R = 34\,700$ h. Keep that in mind.

### 1.2 Deformation, $P'_{LM} = T\,(10 - \log_{10}\dot\varepsilon_s)$, $\dot\varepsilon_s$ in 1/h

Hypothesis: neglect the instantaneous strain $\varepsilon_0$ and the primary strain $\varepsilon_t$, so all of $\varepsilon_{max}$ is spent in secondary creep at constant rate. The **allowable** rate is then

$$\dot\varepsilon_{allow} = \varepsilon_{max}/t = 0.015/8000 = 1.875\cdot10^{-6}\ \text{h}^{-1}.$$

| Margin | Hold fixed | Solve for | Result |
|--------|------------|-----|------------------------------|
| stress | $T$, $\dot\varepsilon_{allow}$ | $\sigma_{lim}$ | $P'_{LM} = 823\,(10 + 5.73) = 12.94\cdot10^3$ → curve → $\sigma_{lim} = 105$ MPa, $\xi'_\sigma = 1.9$ |
| strain | $T$, $\sigma = 55$ MPa, $t$ | $\varepsilon_s$ | curve → $P'_{LM} = 13.7\cdot10^3$, $\log_{10}\dot\varepsilon_s = 10 - 13.7\cdot10^3/823 = -6.65$, $\dot\varepsilon_s = 2.24\cdot10^{-7}$ 1/h, $\varepsilon_s = 0.18$ %, $\xi'_\varepsilon = 8.3$ |

($\dot\varepsilon_s = 2.27\cdot10^{-7}$ 1/h without rounding the logarithm; the margin is
8.3 either way.)

### 1.3 Temperature margin against deformation: which strain rate?

The margin needs $T_{lim} = P'_{LM}/(10 - \log_{10}\dot\varepsilon_s)$ with
$P'_{LM} = 13.7\cdot10^3$ (from $\sigma = 55$ MPa). Which $\dot\varepsilon_s$ goes in:
the allowable $1.875\cdot10^{-6}$ or the actual $2.24\cdot10^{-7}$ h$^{-1}$?

**The allowable one is the coherent choice.** The question is "how hot can the beam run, at
the stress it actually carries, before it reaches 1.5 % in 8000 h?". Hold $\sigma = 55$ MPa
and hold the limit condition, $\dot\varepsilon_s = \dot\varepsilon_{allow}$. Solve for $T$:

$$T_{lim} = \frac{13.7\cdot10^3}{10 - \log_{10}(1.875\cdot10^{-6})} = \frac{13.7\cdot10^3}{15.73} = 871\ \text{K},
\qquad \Delta T = 48\ \text{K},\qquad \xi'_T = 1.06 .$$

**The actual rate gives no information.** $2.24\cdot10^{-7}$ h$^{-1}$ was itself *computed*
from $P'_{LM} = 13.7\cdot10^3$ at $T = 823$ K. Putting it back into the same relation can only
return 823 K: $T_{lim} = T$ by construction, a tautology. With rounded numbers you may
get 825 K, and so an apparent margin of 2 K: that comes from rounding alone.

**The same check on the rupture side.** §1.1 held $t = 8000$ h, the requirement. Holding the
predicted $t_R = 34\,700$ h instead would also give back 823 K. The allowable rate plays the
role of the required life: it *is* the requirement, written as a rate.

**Check it.** At $T = 871$ K and $\sigma = 55$ MPa, $\log_{10}\dot\varepsilon_s =
10 - 13.7\cdot10^3/871 = -5.73$, i.e. $\dot\varepsilon_s = 1.875\cdot10^{-6}$ h$^{-1}$: exactly
1.5 % in 8000 h. A 48 K rise multiplies the creep rate by about 8.

### 1.4 The other margins: strain rate and time

With the hypothesis of §1.2 (linear secondary creep only), on deformation:

- **strain rate:** $\xi'_{\dot\varepsilon} = \dot\varepsilon_{allow}/\dot\varepsilon_s = 1.875\cdot10^{-6}/2.24\cdot10^{-7} = 8.3$;
- **time:** $t_{lim} = \varepsilon_{max}/\dot\varepsilon_s \approx 66\,000$ h, $\xi'_t = 8.3$.

Strain, strain rate and time margins coincide, because $\varepsilon_s = \dot\varepsilon_s\,t$
is linear in both. A real primary stage would spend part of the 1.5 % early, and all three
would drop.

### 1.5 Summary: which failure mode governs?

| Margin | Rupture | Deformation |
|---|---|---|
| stress | 1.55 | 1.9 |
| time | 4.3 | 8.3 |
| temperature | 1.03 ($\Delta T = 22$ K) | 1.06 ($\Delta T = 48$ K) |

Rupture has the smaller margin in every row, so **rupture governs** this beam, and the
quantity to watch is temperature.

### 1.6 Which margin decides, and how much is enough?

Both failure modes have to be checked, and the design is governed by the one closest to
**its own** limit. Compare margins on the same quantity only: $\xi_T$ is a ratio of absolute
temperatures and always sits close to 1, so for temperature read $\Delta T$. And the
smaller margin does not necessarily govern, because the Code asks for more margin against
rupture than against deformation. The right comparison is the margin obtained against the
margin required:

| | $\xi_\sigma$ obtained | $\xi_\sigma$ required | utilisation = required/obtained |
|---|---|---|---|
| rupture | 1.55 | 1.5 | **0.97** |
| deformation | 1.9 | 1.0 | 0.53 |

$\xi = 1$ means the limit is reached exactly at the end of life, with no margin; $\xi < 1$
is not acceptable. The required values come from the ASME Code:

- **Section II, Part D, Mandatory Appendix 1, 1-100(b)** (2010 metric edition, pp. 839-840).
  In the creep range the allowable stress $S$ of Tables 1A and 1B is the lowest of
  100 % of the average stress for a creep rate of 0.01 %/1000 h ($10^{-7}$ h$^{-1}$, about
  1 % in 100 000 h), $100F_{avg}$ % of the average stress to rupture in 100 000 h
  ($F_{avg} = 0.67$ at 815°C and below), and 80 % of the minimum stress to rupture in
  100 000 h. As margins: $\xi_\sigma \geq 1.0$ on creep rate, $\geq 1.5$ on average
  rupture, $\geq 1.25$ on minimum rupture.
- **Section III, Division 5, HBB-3221(b)(1)** (2015 edition, p. 59). For nuclear components
  at elevated temperature, $S_t$ is the lesser of 100 % of the average stress for a total
  strain (elastic, plastic, primary and secondary creep) of 1 %, 80 % of the minimum stress
  for the onset of tertiary creep, and 67 % of the minimum stress to rupture.
- **Section III, Division 5, Nonmandatory Appendix HBB-T, HBB-T-1310** (2015 edition,
  pp. 163-164). Accumulated inelastic strain: 1 % averaged through the thickness, 2 % at the
  surface from the equivalent linear distribution, 5 % locally.

Applied to the beam:

- **rupture:** the master curve runs through the middle of the scatter, so it is an average
  curve and the criterion is $\xi_\sigma \geq 1.5$. 1.55 passes, just. A minimum curve would
  sit lower and the margin would shrink.
- **deformation:** the 1.5 % limit is given by the problem. Division 5 would allow 1 %
  through the thickness, which lowers $\dot\varepsilon_{allow}$ to $1.25\cdot10^{-6}$
  h$^{-1}$ and $\xi'_\sigma$ with it.
- **time and temperature:** the Code sets no explicit factor on either. The time margin is
  already inside the stress factor ($\xi_\sigma = 1.5$ corresponds here to $\xi_t \approx 4$).
  Temperature is covered by requiring the design temperature to bound the metal temperature
  from above. Since 22 K use up the whole life, $\xi_T = 1.03$ is acceptable only if 550°C is
  a true maximum and not an average.

The Code puts the factor on stress and asks for conservatism on temperature, because creep
has little tolerance for temperature errors.

## 2. Second exercise: lower the design temperature by 25°F

A pressure-vessel component designed at 1200°F (649°C) for 100 000 h. What life at
1175°F (635°C), that is 25°F (13.9 K) lower?

The parameter in Rankine, $T(°\text{R}) = T(°\text{F}) + 459.67$ (460 is often used):

$$P_{LM} = 1660\,(20 + 5) = 41\,500, \qquad 20 + \log_{10} t = 41\,500/1635 = 25.38,
\qquad t \approx 241\,000\ \text{h}.$$

A 2.4-fold life for 14 K. Note that the units cancel: equating the parameter at the two
temperatures gives $20 + \log_{10} t_2 = (T_1/T_2)(20 + \log_{10} t_1)$, and only the
**ratio** of absolute temperatures enters. Kelvin gives the same answer as Rankine; °C or °F
would not.

## 3. Third exercise: post-weld heat treatment budget

A 2.25Cr-1Mo shell needs PWHT at 1300°F (704°C) for 4 h. Fabricator: two PWHTs (8 h); user:
three more for repairs (12 h); 20 h in total, which is what the plates are guaranteed for.
During the second PWHT the temperature spiked to 1325°F (718°C) for 2 h. How many hours
are left for the user?

The idea: PWHT is a time-temperature exposure, just like creep, so 2 h at 1325°F are worth
more than 2 h at 1300°F. Convert them to the **equivalent time** at 1300°F with the same
$P_{LM}$:

$$P_{LM} = 1785\,(20 + \log_{10} 2) = 36\,240, \qquad
20 + \log_{10} t_{eq} = 36\,240/1760 = 20.59, \qquad t_{eq} = 3.9\ \text{h}.$$

Used: first PWHT 4 h, second 2 h at 1300°F + 3.9 h equivalent, so 9.9 h. **Left: 10.1 h**,
two full PWHTs and part of a third.

Adding equivalent times is a linear damage sum (Robinson's time-fraction rule): it assumes
that the order of the exposures does not matter.
