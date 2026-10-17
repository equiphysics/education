"""Published results from Vera et al. (2019), for comparison. NA = not reported."""

GLOBAL = {  # Results, "General physiological parameters"
    "no_gravity": dict(CO_L_min=33, EF_pct=65, SV_ml=820, SBP=114, DBP=70, PP=44, MAP=93, TVR=0.17),
    "gravity": dict(CO_L_min=30, EF_pct=59, SV_ml=740, SBP=131, DBP=88, PP=43, MAP=111, TVR=0.22),
}

PWV = {"no_gravity": 5.3, "gravity": 5.2, "in_vivo": 5.27}   # m/s, aorta

CO_DISTRIBUTION = {  # Table 2, % of cardiac output
    "no_gravity": dict(heart=4.2, brain=15.4, muscle=7.7, kidney=18.2, splanchnic=28.3, other=26.2),
    "gravity": dict(heart=5.4, brain=10.5, muscle=11.3, kidney=20.7, splanchnic=32.6, other=19.5),
    "reference": dict(heart=5, brain=10, muscle=15, kidney=20, splanchnic=30, other=20),
}

LOCATION_ORDER = ["Prox Ao", "Dist Ao", "CCA", "MA", "EIA"]

TABLE3 = {  # Womersley number, max wall shear (Pa), mean convective acceleration (1e-5 m^3/s^2), Reynolds
    "alpha": [35.47, 15.05, 6.02, 3.78, 8.02],
    "tau_max": {"gravity": [2.72, 2.89, 2.28, 1.74, 1.50], "no_gravity": [3.05, 3.11, 2.09, 1.79, 1.70]},
    "conv_mean": {"gravity": [57.32, -27.75, -0.12, 0.27, -1.02], "no_gravity": [68.67, -31.55, 6.79, 0.06, -1.32]},
    "Re": {"gravity": [2404, 870, 1160, 98, 278], "no_gravity": [2660, 749, 2312, 68, 195]},
}

TABLE4 = {  # model values and in vivo measurements
    "peak_U": {"in_vivo": [0.742, None, 0.846, 0.403, 0.457],
               "no_gravity": [0.955, 0.834, 1.544, 0.464, 0.642],
               "gravity": [0.731, 0.765, 1.253, 0.395, 0.560]},
    "MAP": {"in_vivo": [104.5, 119.7, 116.9, None, None],
            "no_gravity": [92.82, 94.63, 88.61, 93.54, 94.77],
            "gravity": [110.74, 95.74, 64.04, 132.34, 105.54]},
    "SBP": {"in_vivo": [116.7, 134.4, 134.8, None, None],
            "no_gravity": [113.62, 160.76, 145.08, 160.68, 174.93],
            "gravity": [131.11, 159.78, 103.44, 190.17, 175.73]},
    "DBP": {"in_vivo": [92.2, 109.8, 101.9, None, None],
            "no_gravity": [69.50, 66.70, 61.00, 67.70, 66.38],
            "gravity": [87.75, 69.30, 44.63, 103.78, 78.61]},
    "PP": {"in_vivo": [24.0, 24.2, 32.8, None, None],
           "no_gravity": [44.12, 94.06, 84.08, 92.97, 108.55],
           "gravity": [43.36, 90.47, 58.81, 86.39, 97.13]},
}
# In vivo: peak velocities and carotid pressures in standing horses (mean of 5);
# aortic pressures in one anaesthetized horse lying on its back.
