# Stage 0: Whole-Manuscript Diagnosis and Redevelopment Plan

Source document: B.Eng. project report, "Free Space Optical (FSO) Communication Under Different Weather Conditions" (43 pp., 2022).
Knowledge boundary for the rewrite: literature and standards available on or before 31 December 2021.

---

## 1. What the original work actually contains

The report must be judged on what was built and measured, not on its title.

| Item | What the report states or shows |
|---|---|
| Transmitter | LM386 audio amplifier (gain set to 200 with 10 uF across pins 1 and 8), 9 V battery, visible laser diode driven by the amplifier output. Audio source: .mp3 file from a phone via 3.5 mm jack. |
| Modulation | Analog intensity modulation of the laser by the audio waveform. No digital data, no bit rate, no BER measurement. |
| Receiver | Small solar panel used as a large-area photodetector, coupling capacitor, LM386 amplifier, loudspeaker. |
| Link length | 10 to 20 m stated as the working range. The rain test distance is not stated. |
| "Rain" | Water poured by hand from a plastic bottle through a perforated plastic colander held above the beam (Plate 3.4). |
| Independent variable | "Shower radius" of 3.0, 3.7, 3.8 and 4.0 mm (Fig. 4.1). It is unclear whether this is the hole radius or an estimated drop radius. |
| Measurements | One reading per condition: 1.4, 1.3, 1.2, 1.0 V at the receiver. "2 V transmitted" measured at the transmitter. The clear-channel received voltage is not reported as a number. |
| Analysis | None beyond "bigger radius, lower voltage." No equations, no uncertainty, no repetition. |

Converting the readings to optical loss (receiver output voltage is proportional to photocurrent, which is proportional to received optical power, so loss in dB is 10 log10 of the voltage ratio):

| Shower | Radius (mm) | V_rx (V) | Extra loss vs. Shower A (dB) | Hole area vs. A (if radius = hole) |
|---|---|---|---|---|
| A | 3.0 | 1.4 | 0.00 | 1.00 |
| B | 3.7 | 1.3 | 0.32 | 1.52 |
| C | 3.8 | 1.2 | 0.67 | 1.60 |
| D | 4.0 | 1.0 | 1.46 | 1.78 |

The total spread is about 1.5 dB. That is a real, measurable effect, and it is enough for a short experimental paper if it is framed honestly and backed by physics.

## 2. Critical weaknesses (ranked by how fast a reviewer would reject on them)

### 2.1 Research integrity (must fix before anything else)

1. The abstract reproduces the published abstract of A. Malik and P. Singh, "Free space optics: Current applications and future challenges," Int. J. Opt., 2015, almost word for word ("FSO is a communication system where free space acts as medium between transceivers ... in hours and in lesser economy"). Any journal similarity check will flag it.
2. Section 2.2 (history) is copied from M. Garlinska et al., Future Internet, vol. 12, no. 11, 2020. Page headers from that article ("Future Internet 2020, 12, 179 5 of 18", "11 of 18") survive inside the text.
3. Several citations point to the wrong source. Masers (1954) are cited to Chappe (1824). Lasers are cited to Oersted (1820). The claim of 100 Gb/s FSO is cited to Singer (1959). Flashing signal lamps are cited to "Bell, 1820." These are citation-chain errors inherited from copying.
4. References that have nothing to do with the claims they support: an IoT pricing survey, a 6G survey, an underwater optical survey, a safety informatics paper, a NATO battle-management note.

Fix: the history section is cut to two sentences in the Introduction. The abstract and every section are rewritten from scratch. All references are replaced with verified sources (see `references/verified_references.md`).

### 2.2 Scientific errors

1. Raindrop radius is given as "100 to 1000 nm." Raindrops range from about 0.1 mm to about 4 mm in radius. The stated range is off by three orders of magnitude and would place raindrops in the fog regime.
2. "The rain scattering coefficient can be calculated using Stroke Law." Stokes' law gives the drag and terminal velocity of a small sphere. It is not a scattering law. Rain extinction follows from geometric optics (extinction efficiency near 2) integrated over the drop size distribution.
3. "It is supposed that atmospheric attenuation is wavelength dependent but this is not true" is followed two lines later by "Haze is wavelength dependent." The paragraph contradicts itself. The correct statement depends on particle size relative to wavelength (Rayleigh, Mie, geometric regimes).
4. "Due to the inverse square law, light intensity decreases by square of the distance" is applied to a collimated laser. For a Gaussian beam, the far-field spot grows linearly with range and geometric loss follows the aperture-to-spot area ratio. The inverse square law applies only beyond the Rayleigh range and only as a limit.
5. "Lasers have unlimited range" is not a physical statement and must go.
6. The abstract mentions "hybrid FSO." Nothing hybrid (RF/FSO) was built or analysed.
7. The results section claims "the conclusions ... are totally justified" with four single-shot readings and no uncertainty.

### 2.3 The central physical interpretation is probably wrong, and fixing it becomes the paper's main scientific contribution

The report concludes that larger drops cause more attenuation. Geometric-optics theory says the opposite at fixed water content.

For drops much larger than the wavelength, the extinction efficiency Q_ext is close to 2, so the extinction coefficient is

    beta = sum over drops of Q_ext * pi * r^2 * N  ≈ 2 * pi * r^2 * N

For a fixed liquid water content W (kg/m^3), the number density is N = 3W / (4 pi r^3 rho_w), which gives

    beta ≈ 3W / (2 rho_w r)

So at the same amount of water in the beam, larger drops attenuate **less**, as 1/r. The observed increase in loss must therefore come from something that grows with the "shower radius" faster than 1/r falls. The obvious candidate is water throughput. If the radius is the colander hole radius, the hole area grows by 78% from A to D, the volume flux grows with it, and the liquid water content in the beam grows roughly in proportion. The photograph also shows continuous streams rather than separated drops, which increases the fraction of the beam that is geometrically blocked.

A second effect matters here. A large-area solar-panel receiver has a wide field of view. Half of the extinction by large drops is near-forward diffraction, and a wide-FOV receiver at short range recaptures much of it. The measured loss is therefore lower than the textbook extinction value, which is consistent with the small (1.5 dB) spread.

This turns a weak "bigger is worse" result into a defensible statement: in a gravity-fed rain emulator, the controlling variable is water throughput (liquid water content along the path), not drop size, and the receiver field of view sets how much of the theoretical extinction is observed. Reviewers reward this kind of correction.

### 2.4 Scope mismatch

The title promises "different weather conditions." The experiment covers one emulated condition (rain). Fog, haze, snow and turbulence appear only as copied background text. The objectives list "calculating total attenuation on a rainy day and scintillation on clear days" and "studying performance at different wavelengths, beam divergence, aperture, and range," none of which were done.

Fix, without changing the research direction: keep rain emulation as the experimental core, and deliver the promised multi-weather analysis through a transparent analytical link-budget study (Kruse, Kim and Al Naboulsi for fog and haze, empirical rain models, log-normal and gamma-gamma turbulence, geometric and pointing loss) evaluated for the actual testbed parameters and for representative 850 nm and 1550 nm links. That fulfils the original objectives with methods that existed before 2022.

### 2.5 Missing experimental information

A methods section cannot be written for reproducibility without these. See Section 5 for the list sent to the author.

## 3. Proposed title

**Experimental Emulation of Rain Attenuation on a Low-Cost Short-Range Free-Space Optical Link and Analytical Assessment Under Fog, Haze, Rain and Turbulence**

Shorter alternative for letters-type journals: **Rain Emulation on a Low-Cost Free-Space Optical Link: Measurement, Physical Interpretation and Weather-Dependent Link Budget**

## 4. Target structure (journal article, about 8,000 words)

| # | Section | Built from | Status |
|---|---|---|---|
| | Title, Abstract, Index Terms | Rewritten last, once results are final | Pending |
| I | Introduction | Ch. 1 + parts of Ch. 2 | **Drafted (this round)** |
| II | Related Work (thematic) | Ch. 2.4, replaced | Next |
| III | Channel and Link Model | New: Beer–Lambert, Rayleigh/Mie/geometric regimes, Kruse, Kim, Al Naboulsi, rain models, log-normal and gamma-gamma, beam divergence, pointing error, link budget, SNR and BER for IM/DD OOK | Planned |
| IV | Experimental Testbed and Rain-Emulation Protocol | Ch. 3, rewritten, LM386 pin-by-pin detail moved to a short table | Planned, needs author data |
| V | Results and Discussion | Ch. 4 + new analytical results | Planned |
| VI | Limitations and Future Work | Ch. 5.2, expanded | Planned |
| VII | Conclusion | Ch. 5.1, rewritten | Planned |
| | References (IEEE style, all ≤ 2021) | Replaced | Started |

Material removed entirely: talking drums, smoke signals, runners and pigeons, COVID-19, BNC/STP connector description, the 60-million-subscribers claim (no source), the train-passenger bandwidth example (no source), "LightPointe's unique multibeam system" (vendor marketing), and the recommendation that "students and lecturers" do more research.

## 5. Information needed from the author

Items marked (critical) block the Methods and Results sections.

1. (critical) Received voltage on the clear channel, with no water, at the same distance and settings. Plate 4.1 shows the trace but not the volts/div setting.
2. (critical) What "shower radius" means: colander hole radius, measured drop radius, or something else. How was it measured?
3. (critical) Link distance during the rain test, and the length of beam path exposed to falling water.
4. (critical) Were A to D four different colanders or shower heads? Was the same volume of water poured each time, and over how many seconds?
5. Laser: colour or wavelength (red module, 650 nm?), rated power (e.g. < 5 mW), and any lens or collimator.
6. Solar panel: dimensions or active area, and its rated voltage.
7. What was on the oscilloscope: peak-to-peak or amplitude, and was the input a test tone or music? A tone gives a stable reading.
8. Were readings repeated? Even three repeats per condition allow a mean and standard deviation.
9. Test date and indoor temperature, if recorded.
10. Can the experiment be repeated? A one-day repeat with a fixed pour volume, a timer and five repeats per condition would raise the paper from "demonstration" to "measurement." This is the single most valuable improvement available.

If items 1 to 4 are unavailable, the paper still works, but results must be reported relative to Shower A (the 0.00 to 1.46 dB column above), and the limitation stated plainly.
