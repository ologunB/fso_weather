"""Case study for Paper 2: FSO availability against rain and dust haze in Nigeria.

Reuses the channel models of fso_models.py. Every number quoted in
Section VI of Paper 2 comes from this script.

Run:  python3 analysis/paper2_case_study.py
Outputs: figures/p2_*.png and analysis/paper2_results.json
"""
import json
import math
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import optimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fso_models as fm  # noqa: E402

ROOT = fm.ROOT
FIG = fm.FIG
C, LS, INK, INK2 = fm.C, fm.LS, fm.INK, fm.INK2

# Rain laws, dB/km
def carbonneau(R):
    return 1.076 * R ** 0.67

def soni_tropical(R):
    # Soni et al. 2023, rain chamber, 1550 nm, rain rates up to 210 mm/h
    return 0.63 * R ** 0.91

# One-minute rain rates exceeded 0.01% of an average year (mm/h)
SITES = [
    ("SW region, low (TRMM)", 77.0),
    ("Minna (gauge)", 89.0),
    ("SW region, high (TRMM)", 110.0),
    ("SE region, high (TRMM)", 125.0),
    ("Ota (gauge)", 141.0),
]

# Terminals: T1 is the representative terminal of Paper 1.
# T2 is an illustrative high-end terminal with amplified 1550 nm source and tracking.
T1 = dict(Pt_dBm=13.0, theta=2e-3, DT=0.025, DR=0.08, Lopt_dB=3.0, S_dBm=-35.0)
T2 = dict(Pt_dBm=23.0, theta=0.5e-3, DT=0.025, DR=0.10, Lopt_dB=3.0, S_dBm=-40.0)

def rng(beta, p):
    return fm.max_range(beta, p)

def main():
    res = {"sites": []}
    for name, R in SITES:
        row = {"site": name, "R001": R, "carb_dBkm": carbonneau(R), "soni_dBkm": soni_tropical(R),
               "mp2_dBkm": fm.beta_rain_mp(R), "mp1_dBkm": fm.beta_rain_mp(R, 1.0)}
        for tn, t in (("T1", T1), ("T2", T2)):
            row[f"{tn}_carb_m"] = rng(row["carb_dBkm"], t)
            row[f"{tn}_soni_m"] = rng(row["soni_dBkm"], t)
        res["sites"].append(row)

    # Clear-air ranges of the two terminals (Kim model, V = 20 km, 1550 nm)
    b_clear = fm.beta_vis(20, 1550, fm.q_kim)
    res["clear"] = {"T1_m": rng(b_clear, T1), "T2_m": rng(b_clear, T2)}
    res["geo_1km"] = {"T1": fm.geo_loss_db(1000, T1["theta"], T1["DT"], T1["DR"]),
                      "T2": fm.geo_loss_db(1000, T2["theta"], T2["DT"], T2["DR"])}

    # FSO vs mmWave rain loss over 1 km at Minna (R0.01 = 89 mm/h)
    R = 89.0
    res["minna_1km"] = {"FSO_carb": carbonneau(R), "FSO_soni": soni_tropical(R),
                        "mmW_26_H": 19.85, "mmW_26_V": 15.94, "mmW_38_H": 28.09, "mmW_38_V": 24.25}

    # Dust haze bounding cases (Kim model as haze, and a x7 dust factor)
    dust = []
    for V in (0.5, 1.0, 2.0):
        for lam in (850, 1550):
            b = fm.beta_vis(V, lam, fm.q_kim)
            dust.append({"V_km": V, "lam": lam, "kim_dBkm": b, "x7_dBkm": 7 * b,
                         "T2_kim_m": rng(b, T2), "T2_x7_m": rng(7 * b, T2),
                         "T1_kim_m": rng(b, T1), "T1_x7_m": rng(7 * b, T1)})
    res["dust"] = dust

    # Ratio of Soni to Carbonneau across the Nigerian band
    res["soni_over_carb"] = {str(R): soni_tropical(R) / carbonneau(R) for R in (77, 110, 141)}
    # Crossing rate where the two laws agree
    res["laws_cross_R"] = optimize.brentq(lambda r: soni_tropical(r) - carbonneau(r), 0.5, 50)

    with open(os.path.join(ROOT, "analysis", "paper2_results.json"), "w") as f:
        json.dump(res, f, indent=1)

    # ---------------- Figures ----------------
    # P2 Fig: rain laws with Nigerian band
    Rr = np.linspace(1, 160, 300)
    fig, ax = plt.subplots(figsize=(3.5, 2.8))
    ax.axvspan(77, 141, color="#f4f3f0", zorder=0)
    ax.text(109, 3, "Nigerian $R_{0.01}$\n77 to 141 mm/h", ha="center", fontsize=7, color=INK2)
    ax.plot(Rr, carbonneau(Rr), color=C[0], ls=LS[0], label="Carbonneau (temperate fit)")
    ax.plot(Rr, soni_tropical(Rr), color=C[1], ls=LS[1], label="Soni et al. (tropical chamber)")
    ax.plot(Rr, [fm.beta_rain_mp(r) for r in Rr], color=C[2], ls=LS[2], label="Marshall-Palmer, $Q_{ext}$=2")
    ax.plot(Rr, [fm.beta_rain_mp(r, 1.0) for r in Rr], color=C[3], ls=LS[3], label="Marshall-Palmer, $Q_{ext}$=1")
    ax.set_xlim(0, 160); ax.set_ylim(0, None)
    ax.set_xlabel("Rainfall rate R (mm/h)"); ax.set_ylabel("Specific attenuation (dB/km)")
    ax.legend(loc="upper left", fontsize=7)
    fig.savefig(os.path.join(FIG, "p2_rain_laws.png")); plt.close(fig)

    # P2 Fig: 99.99% range by site (grouped bars, 4 series)
    names = [s["site"] for s in res["sites"]]
    series = [("T1, Carbonneau", "T1_carb_m"), ("T1, Soni", "T1_soni_m"),
              ("T2, Carbonneau", "T2_carb_m"), ("T2, Soni", "T2_soni_m")]
    x = np.arange(len(names)); w = 0.2
    fig, ax = plt.subplots(figsize=(7.0, 2.9))
    for i, (lab, key) in enumerate(series):
        vals = [s[key] for s in res["sites"]]
        ax.bar(x + (i - 1.5) * w, vals, w * 0.92, color=C[i], label=lab, edgecolor="white", linewidth=0.6)
    ax.set_xticks(x); ax.set_xticklabels([n.replace(" (", "\n(") for n in names], fontsize=7.5)
    ax.set_ylabel("Range at 99.99% availability (m)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.28), ncol=4, fontsize=7.5)
    ax.grid(axis="x", visible=False)
    fig.savefig(os.path.join(FIG, "p2_range_sites.png")); plt.close(fig)

    # P2 Fig: FSO vs mmWave, 1 km at Minna
    labs = ["FSO\n(Carb.)", "FSO\n(Soni)", "26 GHz\nV-pol", "26 GHz\nH-pol", "38 GHz\nV-pol", "38 GHz\nH-pol"]
    m = res["minna_1km"]
    vals = [m["FSO_carb"], m["FSO_soni"], m["mmW_26_V"], m["mmW_26_H"], m["mmW_38_V"], m["mmW_38_H"]]
    cols = [C[0], C[0], C[1], C[1], C[1], C[1]]
    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    bars = ax.bar(range(6), vals, 0.7, color=cols, edgecolor="white")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.8, f"{v:.1f}", ha="center", fontsize=7, color=INK)
    ax.set_xticks(range(6)); ax.set_xticklabels(labs, fontsize=7)
    ax.set_ylabel("Rain loss over 1 km (dB)"); ax.grid(axis="x", visible=False)
    ax.set_ylim(0, max(vals) * 1.15)
    fig.savefig(os.path.join(FIG, "p2_fso_vs_mmw.png")); plt.close(fig)

    # P2 Fig: taxonomy
    fig, ax = plt.subplots(figsize=(7.0, 3.0)); ax.set_axis_off(); ax.grid(False)
    ax.set_xlim(0, 100); ax.set_ylim(-5, 52)
    left = [("Fog and haze\n(Mie scattering)", 38), ("Rain\n(geometric scattering)", 29),
            ("Dust haze\n(Harmattan)", 20), ("Turbulence\n(scintillation, wander)", 11), ("Misalignment\n(sway, platform jitter)", 2)]
    right = [("Wavelength choice, power control,\nhybrid RF / THz back-up", 38),
             ("Rain margin, site-specific rain laws,\nsub-10 GHz RF back-up", 29),
             ("Dust-specific models,\nseasonal planning", 20),
             ("Aperture averaging, diversity,\nadaptive optics, coherent DSP", 11),
             ("Pointing, acquisition and tracking,\nbeam-width optimisation", 2)]
    for (t, y) in left:
        ax.add_patch(plt.Rectangle((1, y), 28, 7, fc="#f4f3f0", ec=INK2, lw=0.8))
        ax.text(15, y + 3.5, t, ha="center", va="center", fontsize=7, color=INK)
    for (t, y) in right:
        ax.add_patch(plt.Rectangle((52, y), 47, 7, fc="#ffffff", ec=C[0], lw=0.8))
        ax.text(75.5, y + 3.5, t, ha="center", va="center", fontsize=7, color=INK)
        ax.annotate("", xy=(51.5, y + 3.5), xytext=(29.5, y + 3.5), arrowprops=dict(arrowstyle="->", color=INK2, lw=0.8))
    ax.text(15, 49, "Impairment", ha="center", fontsize=8, weight="bold", color=INK)
    ax.text(75.5, 49, "Main mitigation reported since 2022", ha="center", fontsize=8, weight="bold", color=INK)
    ax.text(50, -3.5, "Machine-learning prediction and weather-aware link switching apply across all rows", ha="center", fontsize=7, color=C[0])
    fig.savefig(os.path.join(FIG, "p2_taxonomy.png")); plt.close(fig)

    print(json.dumps(res, indent=1, default=float))

if __name__ == "__main__":
    main()
