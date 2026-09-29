"""Channel models, link budget and figures for the FSO weather manuscript.

Every number quoted in Section V of the manuscript is produced by this
script. Models are restricted to those published before 2022.

Run:  python3 analysis/fso_models.py
Outputs: figures/*.png and analysis/results.json
"""
import json
import math
import os

import numpy as np
from scipy import integrate, optimize, special

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figures")
os.makedirs(FIG, exist_ok=True)

# Categorical palette (fixed order) with line styles as secondary encoding.
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
LS = ["-", "--", "-.", ":", (0, (5, 1)), (0, (3, 1, 1, 1)), "-", "--"]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({
    "font.family": "DejaVu Serif", "font.size": 9, "axes.edgecolor": INK2,
    "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "lines.linewidth": 1.8, "legend.frameon": False, "legend.fontsize": 8,
    "savefig.dpi": 300, "savefig.bbox": "tight",
})

DB = 10 / math.log(10)          # 4.343 dB per neper
RHO_W = 1000.0                  # kg/m^3

# --------------------------------------------------------------------------
# Fog and haze: visibility-based models (V in km, lam in nm) -> dB/km
# --------------------------------------------------------------------------
def q_kruse(V):
    if V > 50: return 1.6
    if V > 6: return 1.3
    return 0.585 * V ** (1 / 3)

def q_kim(V):
    if V > 50: return 1.6
    if V > 6: return 1.3
    if V > 1: return 0.16 * V + 0.34
    if V > 0.5: return V - 0.5
    return 0.0

def beta_vis(V, lam, q):
    """Kruse-type specific attenuation in dB/km."""
    return DB * (3.91 / V) * (lam / 550.0) ** (-q(V))

def beta_naboulsi(V, lam, kind):
    """Al Naboulsi advection/convection fog, dB/km (lam in um inside formula)."""
    l = lam / 1000.0
    if kind == "advection":
        s = (0.11478 * l + 3.8367) / V
    else:
        s = (0.18126 * l ** 2 + 0.13709 * l + 3.7502) / V
    return DB * s

# --------------------------------------------------------------------------
# Rain
# --------------------------------------------------------------------------
def beta_rain_carbonneau(R):
    return 1.076 * R ** 0.67          # dB/km

MP_N0 = 8000.0                         # m^-3 mm^-1

def mp_lambda(R):
    return 4.1 * R ** -0.21            # mm^-1

def beta_rain_mp(R, recapture=0.0):
    """Geometric-optics extinction (Q_ext = 2) over Marshall-Palmer DSD, dB/km.
    recapture: fraction of the diffraction half recollected by a wide-FOV receiver
    (0 = narrow FOV, full extinction; 1 = all diffracted light recaptured, Q -> 1)."""
    L = mp_lambda(R)
    # integral of (pi D^2/4) * N0 exp(-L D) dD = pi N0 / (2 L^3)  [mm^2 m^-3]
    area = math.pi * MP_N0 / (2 * L ** 3) * 1e-6      # m^-1 per unit Q
    q_eff = 2.0 - recapture
    return DB * q_eff * area * 1000.0

def lwc_mp(R):
    """Liquid water content of Marshall-Palmer rain, g/m^3."""
    L = mp_lambda(R)
    vol = math.pi * MP_N0 / L ** 4 * 1e-9             # m^3 water per m^3 air
    return vol * RHO_W * 1000.0

def beta_fixed_lwc(W_gm3, r_m, q_ext=2.0):
    """Extinction (m^-1) of monodisperse large drops at fixed LWC W."""
    W = W_gm3 * 1e-3
    return q_ext * 3 * W / (4 * RHO_W * r_m)

# --------------------------------------------------------------------------
# Turbulence and pointing
# --------------------------------------------------------------------------
def rytov(Cn2, lam_nm, L):
    k = 2 * math.pi / (lam_nm * 1e-9)
    return 1.23 * Cn2 * k ** (7 / 6) * L ** (11 / 6)

def gg_params(s2):
    s = math.sqrt(s2)
    a = 1 / (math.exp(0.49 * s2 / (1 + 1.11 * s ** 2.4) ** (7 / 6)) - 1)
    b = 1 / (math.exp(0.51 * s2 / (1 + 0.69 * s ** 2.4) ** (5 / 6)) - 1)
    return a, b

def gg_pdf(h, a, b):
    lg = (math.log(2) + ((a + b) / 2) * math.log(a * b) - special.gammaln(a) - special.gammaln(b))
    return np.exp(lg + ((a + b) / 2 - 1) * np.log(h)) * special.kv(a - b, 2 * np.sqrt(a * b * h))

def ln_pdf(h, s2):
    # log-normal with E[h] = 1, log-irradiance variance s2
    mu = -s2 / 2
    return np.exp(-(np.log(h) - mu) ** 2 / (2 * s2)) / (h * np.sqrt(2 * math.pi * s2))

def qfunc(x):
    return 0.5 * special.erfc(x / math.sqrt(2))

H = np.logspace(-5, 1.5, 6000)

def avg_ber(snr_db, pdf=None):
    g = math.sqrt(10 ** (snr_db / 10))
    if pdf is None:
        return qfunc(g)
    return np.trapezoid(qfunc(g * H) * pdf, H)

def pointing_gain_samples(w_z, a_r, sigma_s, n=400):
    """Normalised pointing gain h_p/A0 on a Rayleigh-distributed radial offset
    grid (Farid and Hranilovic Gaussian-beam model). Returns (gain, weight)."""
    v = math.sqrt(math.pi) * a_r / (math.sqrt(2) * w_z)
    w_eq2 = w_z ** 2 * math.sqrt(math.pi) * special.erf(v) / (2 * v * math.exp(-v ** 2))
    u = (np.arange(n) + 0.5) / n                          # quantiles
    r = sigma_s * np.sqrt(-2 * np.log(1 - u))            # Rayleigh inverse CDF
    return np.exp(-2 * r ** 2 / w_eq2), np.full(n, 1 / n), w_eq2

def avg_ber_pointing(snr_db, pdf, gains, weights):
    g = math.sqrt(10 ** (snr_db / 10))
    tot = 0.0
    for gp, w in zip(gains, weights):
        tot += w * np.trapezoid(qfunc(g * gp * H) * pdf, H)
    return tot

# --------------------------------------------------------------------------
# Link budget
# --------------------------------------------------------------------------
LINK = dict(Pt_dBm=13.0, theta=2e-3, DT=0.025, DR=0.08, Lopt_dB=3.0, S_dBm=-35.0)
TESTBED = dict(Pt_dBm=7.0, theta=1e-3, DT=0.003, DR=0.06, Lopt_dB=1.0, lam=650.0)

def geo_loss_db(L, theta, DT, DR):
    spot = DT + theta * L
    return max(0.0, 20 * math.log10(spot / DR))

def margin_db(L_m, beta_dbkm, p=LINK):
    return (p["Pt_dBm"] - p["Lopt_dB"] - geo_loss_db(L_m, p["theta"], p["DT"], p["DR"])
            - beta_dbkm * L_m / 1000.0 - p["S_dBm"])

def max_range(beta_dbkm, p=LINK):
    f = lambda L: margin_db(L, beta_dbkm, p)
    if f(20000) > 0: return 20000.0
    return optimize.brentq(f, 1.0, 20000.0)

# Visibility classes (upper bound of each class, km), after Kim et al.
VIS = [("Dense fog", 0.05), ("Thick fog", 0.2), ("Moderate fog", 0.5), ("Light fog", 1.0),
       ("Thin fog", 2.0), ("Haze", 4.0), ("Light haze", 10.0), ("Clear", 20.0), ("Very clear", 50.0)]
RAIN = [("Light rain", 2.5), ("Moderate rain", 12.5), ("Heavy rain", 25.0),
        ("Very heavy rain", 50.0), ("Extreme rain", 100.0)]

# Measured data from the original report
MEAS_R = np.array([3.0, 3.7, 3.8, 4.0])
MEAS_V = np.array([1.4, 1.3, 1.2, 1.0])

def main():
    res = {}

    # ---------------- Table: weather classes vs attenuation ----------------
    rows = []
    for name, V in VIS:
        r = {"class": name, "V_km": V}
        for lam in (650, 850, 1550):
            r[f"kim_{lam}"] = beta_vis(V, lam, q_kim)
            r[f"kruse_{lam}"] = beta_vis(V, lam, q_kruse)
        if 0.05 <= V <= 1.0:
            r["nab_adv_1550"] = beta_naboulsi(V, 1550, "advection")
            r["nab_conv_1550"] = beta_naboulsi(V, 1550, "convection")
            r["nab_adv_850"] = beta_naboulsi(V, 850, "advection")
        r["range_850_m"] = max_range(r["kim_850"])
        r["range_1550_m"] = max_range(r["kim_1550"])
        rows.append(r)
    res["visibility_table"] = rows

    rrows = []
    for name, R in RAIN:
        b = beta_rain_carbonneau(R)
        rrows.append({"class": name, "R": R, "carbonneau": b,
                      "mp_narrow": beta_rain_mp(R), "mp_wide": beta_rain_mp(R, 1.0),
                      "lwc_gm3": lwc_mp(R), "range_m": max_range(b)})
    res["rain_table"] = rrows

    # ---------------- Emulator interpretation ----------------
    rel = 10 * np.log10(MEAS_V[0] / MEAS_V)
    res["measured_rel_loss_db"] = rel.tolist()
    res["hole_area_ratio"] = ((MEAS_R / MEAS_R[0]) ** 2).tolist()
    emu = []
    for ell in (0.1, 0.2, 0.3):
        spec = rel[-1] / (ell / 1000.0)                    # dB/km
        beta_np = rel[-1] / DB / ell                       # m^-1
        W_narrow = beta_np * 4 * RHO_W * 2e-3 / (2 * 3) * 1e3   # g/m^3 for r=2 mm, Q=2
        W_wide = beta_np * 4 * RHO_W * 2e-3 / (1 * 3) * 1e3     # Q=1 (full recapture)
        emu.append({"ell_m": ell, "equiv_dBkm": spec, "W_Q2_gm3": W_narrow, "W_Q1_gm3": W_wide})
    res["emulator"] = emu
    res["lwc_100mmh"] = lwc_mp(100.0)

    # ---------------- Turbulence ----------------
    turb = []
    for label, Cn2 in (("Weak", 1e-15), ("Moderate", 1e-14), ("Strong", 1e-13)):
        for lam in (850, 1550):
            s2 = rytov(Cn2, lam, 1000.0)
            a, b = gg_params(s2)
            turb.append({"regime": label, "Cn2": Cn2, "lam": lam, "rytov": s2,
                         "alpha": a, "beta": b, "SI": 1 / a + 1 / b + 1 / (a * b)})
    s2_tb = rytov(1e-13, 650, 10.0)
    res["testbed_rytov_strong_10m"] = s2_tb
    res["turbulence"] = turb

    # BER curves at 1550 nm, 1 km
    snr = np.arange(0, 51, 1.0)
    s2w = rytov(1e-15, 1550, 1000.0)
    s2m = rytov(1e-14, 1550, 1000.0)
    s2s = rytov(1e-13, 1550, 1000.0)
    pdf_ln = ln_pdf(H, s2w)
    am, bm = gg_params(s2m); pdf_gm = gg_pdf(H, am, bm)
    as_, bs = gg_params(s2s); pdf_gs = gg_pdf(H, as_, bs)
    gains, wts, weq2 = pointing_gain_samples(w_z=1.0, a_r=0.04, sigma_s=0.3)
    curves = {
        "No turbulence (AWGN)": [avg_ber(x) for x in snr],
        f"Weak, log-normal ($\\sigma_R^2$={s2w:.3f})": [avg_ber(x, pdf_ln) for x in snr],
        f"Moderate, gamma-gamma ($\\sigma_R^2$={s2m:.2f})": [avg_ber(x, pdf_gm) for x in snr],
        f"Strong, gamma-gamma ($\\sigma_R^2$={s2s:.2f})": [avg_ber(x, pdf_gs) for x in snr],
        "Strong + pointing jitter ($\\sigma_s$=0.3 m)": [avg_ber_pointing(x, pdf_gs, gains, wts) for x in snr],
    }
    def snr_at(target, ys):
        ys = np.array(ys)
        idx = np.where(ys <= target)[0]
        if len(idx) == 0: return None
        i = idx[0]
        if i == 0: return float(snr[0])
        x0, x1 = snr[i - 1], snr[i]; y0, y1 = math.log10(ys[i - 1]), math.log10(ys[i])
        return float(x0 + (math.log10(target) - y0) * (x1 - x0) / (y1 - y0))
    res["snr_for_1e-6"] = {k: snr_at(1e-6, v) for k, v in curves.items()}
    res["snr_for_1e-3"] = {k: snr_at(1e-3, v) for k, v in curves.items()}
    res["pointing_weq_m"] = math.sqrt(weq2)

    # Testbed geometric check
    res["testbed_spot_10m_mm"] = (TESTBED["DT"] + TESTBED["theta"] * 10) * 1000
    res["testbed_spot_20m_mm"] = (TESTBED["DT"] + TESTBED["theta"] * 20) * 1000
    res["testbed_fog_loss_10m_dense_db"] = beta_vis(0.05, 650, q_kim) * 0.01
    res["testbed_rain_loss_10m_100mmh_db"] = beta_rain_carbonneau(100) * 0.01
    res["clear_margin_1550_1km"] = margin_db(1000, beta_vis(20, 1550, q_kim))
    res["geo_loss_1km"] = geo_loss_db(1000, LINK["theta"], LINK["DT"], LINK["DR"])

    with open(os.path.join(ROOT, "analysis", "results.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)

    # =========================== FIGURES ===========================
    # Fig 3: fog/haze attenuation vs visibility
    V = np.logspace(np.log10(0.05), np.log10(20), 300)
    fig, ax = plt.subplots(figsize=(3.5, 2.8))
    ax.loglog(V, [beta_vis(v, 1550, q_kruse) for v in V], color=C[0], ls=LS[0], label="Kruse, 1550 nm")
    ax.loglog(V, [beta_vis(v, 1550, q_kim) for v in V], color=C[1], ls=LS[1], label="Kim, 1550 nm")
    ax.loglog(V, [beta_vis(v, 850, q_kim) for v in V], color=C[2], ls=LS[2], label="Kim, 850 nm")
    Vn = V[V <= 1.0]
    ax.loglog(Vn, [beta_naboulsi(v, 1550, "advection") for v in Vn], color=C[3], ls=LS[3], label="Al Naboulsi adv., 1550 nm")
    ax.set_xlabel("Visibility V (km)"); ax.set_ylabel("Specific attenuation (dB/km)")
    ax.legend(loc="upper right")
    fig.savefig(os.path.join(FIG, "fig3_fog_models.png")); plt.close(fig)

    # Fig 4: rain attenuation vs rain rate
    R = np.linspace(1, 150, 300)
    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    ax.plot(R, beta_rain_carbonneau(R), color=C[0], ls=LS[0], label="Carbonneau power law")
    ax.plot(R, [beta_rain_mp(r) for r in R], color=C[1], ls=LS[1], label="Marshall-Palmer, $Q_{ext}$=2")
    ax.plot(R, [beta_rain_mp(r, 1.0) for r in R], color=C[2], ls=LS[2], label="Marshall-Palmer, $Q_{ext}$=1")
    ax.set_xlabel("Rainfall rate R (mm/h)"); ax.set_ylabel("Specific attenuation (dB/km)")
    ax.set_xlim(0, 150); ax.set_ylim(0, None); ax.legend(loc="upper left")
    fig.savefig(os.path.join(FIG, "fig4_rain_models.png")); plt.close(fig)

    # Fig 5: measured results (two panels, one axis each)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.5))
    a1.plot(MEAS_R, MEAS_V, color=C[0], marker="o", ms=5)
    for r_, v_, n_ in zip(MEAS_R, MEAS_V, "ABCD"):
        a1.annotate(n_, (r_, v_), textcoords="offset points", xytext=(5, 3), color=INK2, fontsize=8)
    a1.set_xlabel("Emulator radius (mm)"); a1.set_ylabel("Received amplitude (V)")
    a1.set_ylim(0.8, 1.6); a1.set_title("(a)", fontsize=9, loc="left")
    area = (MEAS_R / MEAS_R[0]) ** 2
    a2.plot(area, rel, color=C[1], marker="s", ms=5)
    for x_, y_, n_ in zip(area, rel, "ABCD"):
        a2.annotate(n_, (x_, y_), textcoords="offset points", xytext=(5, 3), color=INK2, fontsize=8)
    a2.set_xlabel("Hole area relative to setting A"); a2.set_ylabel("Excess loss vs. A (dB)")
    a2.set_title("(b)", fontsize=9, loc="left")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig5_measured.png")); plt.close(fig)

    # Fig 6: extinction vs drop radius at fixed LWC
    rr = np.linspace(0.1, 4.0, 200)
    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    for i, W in enumerate((0.5, 1.33, 4.0)):
        ax.plot(rr, DB * 1000 * beta_fixed_lwc(W, rr * 1e-3), color=C[i], ls=LS[i],
                label=f"W = {W:g} g/m$^3$")
    ax.set_yscale("log"); ax.set_xlabel("Drop radius r (mm)")
    ax.set_ylabel("Specific attenuation (dB/km)"); ax.legend(loc="upper right")
    fig.savefig(os.path.join(FIG, "fig6_lwc_radius.png")); plt.close(fig)

    # Fig 7: BER curves
    fig, ax = plt.subplots(figsize=(3.5, 3.6))
    for i, (k, v) in enumerate(curves.items()):
        ax.semilogy(snr, np.clip(v, 1e-12, 1), color=C[i], ls=LS[i], label=k)
    ax.set_ylim(1e-9, 1); ax.set_xlim(0, 50)
    ax.set_xlabel("Average electrical SNR (dB)"); ax.set_ylabel("Average BER")
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.2), fontsize=7, ncol=1)
    fig.savefig(os.path.join(FIG, "fig7_ber.png")); plt.close(fig)

    # Fig 8: link margin vs distance at 1550 nm
    Ls = np.logspace(1, 4, 300)
    cases = [("Clear (V = 20 km)", beta_vis(20, 1550, q_kim)),
             ("Haze (V = 4 km)", beta_vis(4, 1550, q_kim)),
             ("Heavy rain (25 mm/h)", beta_rain_carbonneau(25)),
             ("Light fog (V = 1 km)", beta_vis(1, 1550, q_kim)),
             ("Moderate fog (V = 0.5 km)", beta_vis(0.5, 1550, q_kim)),
             ("Dense fog (V = 0.05 km)", beta_vis(0.05, 1550, q_kim))]
    fig, ax = plt.subplots(figsize=(3.5, 3.7))
    for i, (k, b) in enumerate(cases):
        ax.semilogx(Ls, [margin_db(L, b) for L in Ls], color=C[i], ls=LS[i], label=k)
    ax.axhline(0, color=INK2, lw=0.8)
    ax.set_ylim(-40, 50); ax.set_xlabel("Link distance (m)"); ax.set_ylabel("Link margin (dB)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.2), fontsize=7, ncol=2)
    fig.savefig(os.path.join(FIG, "fig8_margin.png")); plt.close(fig)

    # Fig 1: system block diagram
    fig, ax = plt.subplots(figsize=(7.0, 2.0)); ax.set_axis_off(); ax.grid(False)
    ax.set_xlim(0, 120); ax.set_ylim(0, 24)
    bw = 15.0
    boxes = [(0.5, "Audio source\n(phone,\n3.5 mm jack)"), (18, "LM386\namplifier\n(gain 200)"),
             (35.5, "Laser diode\n(intensity\nmodulated)"), (69, "Solar-cell\nphoto-\ndetector"),
             (86.5, "LM386\namplifier\n+ coupling C"), (104, "Speaker or\noscilloscope")]
    for x, t in boxes:
        ax.add_patch(plt.Rectangle((x, 7), bw, 12, fc="#f4f3f0", ec=INK2, lw=0.8))
        ax.text(x + bw / 2, 13, t, ha="center", va="center", fontsize=6.8, color=INK)
    for x in (15.5, 33, 84, 101.5):
        ax.annotate("", xy=(x + 2.5, 13), xytext=(x, 13), arrowprops=dict(arrowstyle="->", color=INK2, lw=0.8))
    ax.annotate("", xy=(69, 13), xytext=(50.5, 13), arrowprops=dict(arrowstyle="->", color=C[7], lw=1.6))
    ax.add_patch(plt.Rectangle((56.5, 5), 6, 16, fc="none", ec=C[0], lw=0.8, ls="--"))
    for yy in (7, 10.5, 14, 17.5):
        ax.plot([58.3, 58.3], [yy + 2, yy + 0.8], color=C[0], lw=1)
        ax.plot([60.7, 60.7], [yy + 1.4, yy + 0.2], color=C[0], lw=1)
    ax.text(59.5, 2.2, "rain emulator", ha="center", fontsize=7, color=C[0])
    ax.text(53, 16, "free\nspace", ha="center", fontsize=6.5, color=INK2)
    ax.text(0.5, 21.5, "Transmitter", fontsize=8, color=INK, weight="bold")
    ax.text(69, 21.5, "Receiver", fontsize=8, color=INK, weight="bold")
    fig.savefig(os.path.join(FIG, "fig1_system.png")); plt.close(fig)

    print(json.dumps({k: res[k] for k in ("measured_rel_loss_db", "emulator", "lwc_100mmh",
                     "snr_for_1e-6", "snr_for_1e-3", "testbed_rytov_strong_10m", "pointing_weq_m",
                     "testbed_spot_10m_mm", "testbed_spot_20m_mm", "testbed_fog_loss_10m_dense_db",
                     "testbed_rain_loss_10m_100mmh_db", "clear_margin_1550_1km", "geo_loss_1km")},
                     indent=1, default=float))
    for r in rows:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    for r in rrows:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    for t in turb:
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in t.items()})

if __name__ == "__main__":
    main()
