# Paper 2: Plan (current literature, 2022 onward allowed)

Paper 1 stays frozen at the 2021 knowledge boundary. Paper 2 is a separate, current paper. It must not recycle Paper 1's text, and it should cite Paper 1 once published.

## Option A (recommended): review plus tropical case study

Working title: "Weather-Resilient Free-Space Optical Links for Tropical Regions: A Review of Recent Advances and a Link-Availability Case Study for Southern Nigeria"

Why: a review with a quantitative case study gets cited, needs no new lab time, and uses the analysis code already built.

Proposed outline:
1. Introduction: FSO in 6G backhaul and fronthaul, rural connectivity, and the tropical-weather problem.
2. Recent channel modelling: rain, fog, dust and haze models after 2021, multiple-scattering corrections, data-driven and machine-learning attenuation prediction.
3. Turbulence and pointing: recent statistical models, beam tracking, adaptive optics for terrestrial links.
4. Mitigation: hybrid FSO/RF and FSO/mmWave/THz switching, relaying, diversity, adaptive modulation and coding.
5. Deployments: terrestrial long-range commercial links, drone and HAP-based FSO, ground-to-satellite links, and what their field data say about weather.
6. Case study: link availability for southern Nigeria from measured rainfall and visibility statistics, at 850 and 1550 nm, with and without an RF back-up. Reuses `analysis/fso_models.py`.
7. Open problems and research directions.

## Option B: new experimental paper

Rebuild the testbed with a photodiode receiver and digital OOK, measure flow rate, repeat each condition, and add a fog condition (fog machine or ultrasonic mister). Stronger journal target, but needs one to two weeks of lab work.

## Rules for Paper 2

1. Every post-2021 reference must be verified against a database before it is cited. No reference from memory.
2. Local climate data must come from a named source (NiMet records, GPM/IMERG satellite rainfall, or published studies).

## Decisions needed from the author

1. Option A (review plus case study) or Option B (new experiment)?
2. Is local rainfall or visibility data available (NiMet station records, university weather station)?
3. Target journal or conference, if one is already in mind.
