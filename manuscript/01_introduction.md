# Section I: Introduction

## Step 1. Critical review of the original

The original Chapter 1 (Background, Motivation, Aims and Objectives, Methodology, Scope) runs to about 1,100 words. It opens with a general statement ("The main goal of a communication system is to transfer information"), paraphrases Majumdar (2015) on atmospheric effects, then moves to smartphone demand, a train-passenger bandwidth example, a "60 million people" broadband figure, and a local motivation in Nigeria. It ends with three objectives and a scope of 10 to 20 m.

The chapter reads as a thesis introduction. A journal introduction has a different job: in about one page it must place the work in the literature, name the gap, and state what the paper adds.

## Step 2. Weaknesses

1. No research gap. The chapter never says what is missing in prior work, so the reader cannot judge what this study contributes.
2. No contribution statement. Journals expect an explicit list of contributions.
3. Unsupported numbers. "Almost 60 million people now pay to get data" and "500 to 1300 passengers per train" have no source and do not relate to the experiment.
4. Mixed-up physics. The text states that "atmospheric turbulence happens because of the scattering, absorption, and dispersion due to fog, haze, mist, snow, and rain." Turbulence comes from refractive-index fluctuations driven by temperature gradients, not from particulates. Scattering and turbulence are separate impairments.
5. Objectives the work does not meet. "Calculating scintillation on clear days" and "studying performance at different wavelengths, beam divergence angle, aperture diameters and transmission range" were not done.
6. Weak motivation for FSO versus RF. The comparison is asserted, not argued, and it omits the one comparison that matters most for a weather paper: FSO and millimetre-wave RF fail under different weather.
7. Methodology and Scope sit inside the Introduction. In a journal article they belong in the Methods section.
8. Informal register ("imagine how this data rate demand is difficult to achieve," "a mine waiting to be explored").

## Step 3. Proposed improvements

1. Build the argument in five steps: why FSO, why weather matters, what prior work has done, what is still missing, what this paper does.
2. Replace unsourced statistics with verified, pre-2022 sources.
3. Separate the three impairment families cleanly: absorption and scattering (deterministic, weather-driven), turbulence (random, temperature-driven), and misalignment (mechanical).
4. State the gap precisely: rain-emulation studies seldom control liquid water content separately from drop size, and low-cost reproducible testbeds are scarce.
5. List four concrete contributions tied to what was actually built and what will be computed.
6. Move methodology and scope to Section IV.
7. Keep Nigeria and tropical climates as the application context. It is a real and legitimate motivation.

## Step 4. Rewritten section

> Placeholders: bracketed numbers refer to `references/verified_references.md`. Text marked **[AUTHOR DATA]** needs values from the author (see Stage 0, Section 5). Numerical claims about this study are limited to what the original measurements support.

---

### I. INTRODUCTION

Free-space optical (FSO) communication transmits information through the unguided atmosphere on an intensity-modulated optical carrier, usually in the near-infrared windows around 850 nm and 1550 nm [1], [2]. Terrestrial FSO links operate between fixed line-of-sight terminals over distances from a few tens of metres to several kilometres, and they serve as last-mile access, LAN-to-LAN bridges, fibre back-up, cellular backhaul and rapidly deployable links for disaster recovery [1], [3]. Three properties explain the interest in the technology. The optical spectrum is unlicensed, so links can be installed without a regulatory process. The beam divergence is typically on the order of a milliradian, so neighbouring links cause negligible mutual interference and interception requires physical access to the beam. Finally, the carrier frequency supports data rates in the gigabit-per-second range with compact, low-power terminals [1], [4].

These properties matter most where fibre is expensive or slow to install. Trenching, rights-of-way and the cost of civil works often dominate the cost of a fibre connection in urban areas and between buildings [5]. In many developing regions, including Nigeria, the gap between demand for broadband and the reach of wired infrastructure is wide. A short FSO link that bridges a road, a campus or a group of buildings is a practical way to extend an existing network, provided its availability under local weather is understood.

FSO also complements radio-frequency (RF) systems. Microwave and millimetre-wave links need licensed spectrum, and above roughly 10 GHz they suffer strong rain attenuation because raindrop sizes approach the carrier wavelength. Optical links behave in the opposite way. Fog and haze droplets, with radii of a few micrometres, are comparable to optical wavelengths and dominate optical extinction, while rain causes comparatively moderate optical loss. Nadeem et al. exploited this complementarity and showed that pairing an FSO link with a 40 GHz RF back-up raises the availability of the hybrid system toward carrier-class levels [6]. Any design of this kind depends on accurate weather-dependent loss estimates for the optical path.

The atmosphere degrades an optical link through three separate mechanisms [2], [7]. The first is extinction by absorption and scattering. Molecular absorption is small inside the transmission windows, so scattering by aerosols and hydrometeors dominates. The size parameter x = 2πr/λ, where r is the particle radius and λ the wavelength, sets the scattering regime: Rayleigh scattering by gas molecules (x ≪ 1), Mie scattering by fog and haze droplets (x ≈ 1 to 100), and geometric (non-selective) scattering by raindrops (x ≫ 1). Dense fog is the most severe case, with specific attenuation that reaches the order of 300 dB/km at a visibility near 50 m [8]. Rain is less severe but still significant. Heavy rainfall of about 150 mm/h produces attenuation of 20 to 30 dB/km [9]. The second mechanism is atmospheric turbulence. Temperature gradients create random refractive-index fluctuations, characterised by the structure parameter C_n², which cause scintillation, beam wander and beam spreading even in clear air [10], [11]. The third mechanism is misalignment between the beam and the receiver, caused by building sway and thermal expansion, which adds random pointing loss [12]. These effects differ in time scale and statistics, so they are modelled and mitigated with different tools.

Extinction by fog and haze is predicted with visibility-based empirical models. The Kruse model relates the extinction coefficient to visibility and wavelength [13]. Kim et al. revised the wavelength exponent for low visibility on the basis of measurements at 785 nm and 1550 nm and concluded that, in dense fog, extinction becomes almost independent of wavelength [14]. Al Naboulsi et al. proposed separate relations for advection and convection fog [15], and Grabner and Kvicera derived a wavelength-dependent model from Mie theory that links the slope of the extinction curve to the effective droplet radius [16]. Rain attenuation is usually estimated with a power law in rainfall rate, fitted to measured data, or computed from a drop size distribution such as the Marshall–Palmer distribution [17], [18]. Korai et al. noted that experimental rain data at optical wavelengths remain scarce compared with the large microwave datasets collected by ITU-R, and that published optical rain studies usually cover limited local data rather than long-term statistics [8].

Experimental work falls into two groups. Field campaigns measure received power on commercial terminals while a nearby weather station records visibility or rainfall rate. Examples include rain measurements on a 700 m, 810 nm link in Kuala Lumpur [19] and a measurement setup proposed for tropical conditions in Malaysia [20]. These campaigns capture real weather but require costly equipment and long observation periods, and they cannot repeat a given condition on demand. Controlled-chamber experiments address repeatability. Ijaz et al. generated fog and smoke in an indoor chamber and measured attenuation at several wavelengths against the chamber visibility [21]. Controlled studies have focused mainly on fog and smoke, and comparatively few document rain emulation in enough detail to separate the effect of drop size from the effect of water content along the beam. Geometric-optics theory predicts that, at a fixed liquid water content, extinction by large drops scales inversely with drop radius, so an emulator that changes nozzle or hole size also changes flow rate, and the two effects are easily confounded. In addition, most chamber facilities use laboratory-grade sources and detectors, which leaves a gap for low-cost, reproducible testbeds that resource-limited laboratories can build and use to validate propagation models.

This paper addresses that gap with a low-cost analog FSO link and a simple gravity-fed rain emulator, combined with an analytical model that places the measurements in context. The objectives are: (i) to build and characterise a short-range FSO link from commercially available components; (ii) to measure the received-signal reduction produced by emulated rain at four emulator settings; (iii) to interpret the measurements with extinction theory, taking into account the liquid water content in the beam and the receiver field of view; and (iv) to extend the assessment to fog, haze, rain and turbulence through a link-budget analysis that uses established pre-2022 models.

The main contributions are as follows.

1. A complete, reproducible description of a low-cost FSO testbed that uses an LM386-driven visible laser diode as the transmitter and a solar-cell photodetector with an LM386 amplifier as the receiver. The total component cost is below **[AUTHOR DATA: cost]**.
2. A rain-emulation procedure and measurement set showing that the received signal falls by up to 1.46 dB relative to the lightest emulator setting as the emulator aperture radius increases from 3.0 mm to 4.0 mm **[to be restated against the clear-channel reference once available]**.
3. A physical interpretation, based on geometric-optics extinction, showing that the observed trend is explained by the increase in water throughput and liquid water content along the beam, and by the partial recapture of forward-diffracted light by the wide-field-of-view receiver, rather than by drop size alone. This identifies a confounding factor that affects simple rain emulators and gives a practical rule for designing them.
4. A unified weather-dependent link budget for the testbed at its operating wavelength and for representative 850 nm and 1550 nm links. It combines the Kruse, Kim and Al Naboulsi fog and haze models, empirical rain models, log-normal and gamma-gamma turbulence statistics, geometric loss and pointing loss, and it reports link margin, signal-to-noise ratio, bit error rate and maximum range for each weather class.

The rest of the paper is organised as follows. Section II reviews related work by theme. Section III presents the channel and link model. Section IV describes the testbed and the rain-emulation protocol. Section V presents and discusses the experimental and analytical results. Section VI states the limitations of the study, and Section VII concludes the paper.

---

## Step 5. Why the new version is stronger

1. It follows the structure reviewers expect: context, problem, prior work, gap, objectives, contributions, roadmap. The original had no gap and no contributions.
2. Every factual claim has a verified source published before 2022. The unsourced statistics are gone.
3. The physics is correct. Scattering and turbulence are separated, the size-parameter regimes are defined, and the magnitude of fog and rain loss is quantified.
4. The FSO-versus-RF argument now rests on the complementary weather behaviour documented by Nadeem et al., which ties the motivation directly to the paper's topic.
5. The gap is specific and testable (drop size confounded with water content in rain emulators, and a shortage of low-cost reproducible testbeds). The experiment answers it.
6. The contributions promise only what the data and the planned analysis can deliver. The original objectives on scintillation, wavelength, divergence and aperture are now met through the analytical section rather than left unfulfilled.
7. The Nigerian context remains, stated as an engineering motivation rather than as an unsourced statistic.
8. Length: about 1,250 words, which fits a full-length IEEE or Optica article.

## Open items for this section

- Component cost for contribution 1.
- Contribution 2 will be restated in absolute terms if the clear-channel voltage is available.
- The claim in the gap paragraph that controlled rain studies are comparatively few is framed conservatively. It will be checked against the thematic review in Section II before submission.
