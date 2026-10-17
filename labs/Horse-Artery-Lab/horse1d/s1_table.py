"""S1 Table of Vera et al. (2019): terminal impedance data (CC BY 4.0).

Total terminal resistance R_T (mmHg s/ml) and terminal compliance C_T (ml/mmHg)
for the 62 terminal branches. In the paper's 3-element Windkessel, R1 = Zc (the
terminal vessel's characteristic impedance) and R2 = R_T - R1.

The S1 file lists segment "79b" with the same values as 58b; that is a typo for
69b (79 is the right renal artery, listed separately, and 69b is otherwise missing).
"""

_S1 = """
2 7.22 14.36|3 7.22 14.36|7 32.80 7.97|9 29.82 0.05|11 10.98 7.53|13 32.80 11.01
15 55.44 1.34|17 55.44 0.61|19 55.44 25.80|21 55.44 0.33|23 55.44 6.34|25 67.61 1.31
26 64.46 1.65|28 32.80 3.62|30 29.82 0.05|32 10.98 3.98|35 55.44 11.00|36 55.44 3.78
38 55.44 1.46|40 55.44 25.80|42 55.44 0.33|44 61.60 7.55|46 67.61 1.31|47 64.46 1.65
50 1.10 0.48|51 8.55 0.71|53 8.55 1.50|55 8.62 0.04|57 8.92 0.10|58b 9.00 1.19
59 9.08 0.20|61 1.10 0.48|62 8.55 0.71|64 8.55 1.50|66 8.62 0.04|68 8.92 0.10
70 9.08 0.20|73 3.55 2.78|75 1.96 7.34|77 3.03 4.04|79 1.80 3.62|81 1.80 3.63
83 22.55 0.24|84 22.55 0.24|86 3.51 1.22|88 5.52 21.68|90 47.31 0.66|92 23.13 0.12
94 47.31 2.97|96 47.31 0.65|69b 9.00 1.20|98 47.31 0.07|99b 57.70 6.21|100 57.70 0.47
101 5.52 21.68|103 23.13 0.12|105 55.02 0.70|107 47.31 2.97|109 47.31 0.65|111 47.31 0.07
112b 57.70 6.21|113 52.57 0.47
"""


def load():
    """{segment: (R_T in mmHg s/ml, C_T in ml/mmHg)}; compliance is listed in 1e-2 ml/mmHg."""
    out = {}
    for item in _S1.replace("\n", "|").split("|"):
        if item.strip():
            seg, r, c = item.split()
            out[seg] = (float(r), float(c) * 1e-2)
    return out
