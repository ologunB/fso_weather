# Mock Peer Review: Paper 1

Manuscript: "Experimental Emulation of Rain Attenuation on a Low-Cost Short-Range Free-Space Optical Link and Analytical Assessment Under Fog, Haze, Rain and Turbulence"
Reviewer stance: an Associate Editor for an Optica or IEEE photonics journal, judging against pre-2022 standards.

## Recommendation

Major revision. The analysis and writing are at journal level. The experimental evidence is not, because it rests on four single readings with no dry reference. With the data items listed below, the paper fits journals such as Journal of Optical Communications, Optical and Quantum Electronics, Optik, or an engineering-education venue that values low-cost testbeds. For IEEE Transactions or Optics Express, a repeated campaign with a narrow-FOV photodiode and digital BER measurement would be needed.

## Scores

| Criterion | Score /10 | Comment |
|---|---|---|
| Novelty | 5 | The emulator critique (throughput vs. drop size, FOV recapture, equivalent LWC) is new and useful. The link-budget part applies known models. |
| Originality | 6 | Honest reinterpretation of the authors' own data is a strength. |
| Literature review | 7 | Thematic, balanced, 23 verified references. Would benefit from 5 to 10 more rain-chamber and tropical-measurement papers. |
| Methodology | 4 | No flow rate, no wetted length, no repeats, no dry reference, wavelength and power unconfirmed. |
| Technical depth | 7 | Covers extinction regimes, three fog models, two rain models, LN and GG turbulence, pointing, BER. |
| Mathematical rigor | 7 | Derivations of (10) to (12) are clean and physically interpreted. The GG and pointing expressions are standard. |
| Results | 5 | Analytical results are solid and reproducible. Experimental results are thin. |
| Discussion | 7 | Good engineering implications and design rules. Comparison with prior work is concise. |
| Writing quality | 8 | Clear, structured, no filler. |
| References | 7 | All pre-2022 and verified. A few full author lists still need a publisher check. |
| Publication readiness | 4 | Blocked by the author-data placeholders and the single-shot data. |

## Major comments

1. Report the dry-channel amplitude. Without it, readers cannot judge the total emulator loss.
2. Measure and report the flow rate (mL/s) and the wetted length for each emitter. This turns the throughput argument from inference into measurement.
3. Repeat each condition at least five times and report mean and standard deviation. The B-C difference is currently within reading error.
4. Confirm laser wavelength, power, divergence and solar-cell area. Table IV uses assumed values.
5. Consider one extra condition that holds hole size fixed and changes the number of holes. That single test would confirm the central claim.

## Minor comments

1. Add a local rainfall-rate source for southern Nigeria (pre-2022) in Section V-E.
2. State the oscilloscope volts/div setting used for the readings.
3. Consider adding aperture averaging to Fig. 7, or state its effect qualitatively in the text (already partly done).
4. Confirm the full author lists flagged in `references/verified_references.md`.

## What would raise the score most, in order

1. Five repeats per condition plus a dry reference (one afternoon of lab work).
2. Flow-rate measurement with a measuring jug and a stopwatch.
3. A photodiode receiver with a lens and small field stop, to compare wide and narrow FOV directly.
