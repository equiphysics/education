"""The equine arterial tree from Vera et al. (2019), PLoS ONE 14(8): e0221425.

Table 1 of the paper lists 117 segments: lengths, branching angles, tapered lumen
diameters, and distensibilities. The branching (which segment feeds which) is
read from Fig 1 and from equine anatomy. The paper's data are CC BY 4.0.

Angle convention (from Fig 1, horse facing left): 0 deg points toward the tail,
90 deg straight up, 180 deg toward the head, 270 deg straight down. A segment of
length L at angle phi rises L*sin(phi).
"""

# seg | name | angle (deg) | mean length (mm) | SD | mean diameter (mm) | SD |
#     proximal lumen diameter (mm) | distal lumen diameter (mm) | distensibility (1e-3 / mmHg)
# "-" means no value in the paper.
_TABLE1 = """
1|Aorta ascendens 1|90|18|9|68|6|68.18|67.39|6.85
2|A coronaria sinistra|180|20|-|19|6|23.638|12.10|3.17
3|A coronaria dextra|0|20|-|19|6|23.638|12.10|3.17
4|Aorta ascendens 2|90|64|9|67|6|67.22|66.82|6.80
5|Truncus brachiocephalicus 1|160|38|26|39|9|38.882|38.88|4.90
6|A subclavia sinistra 1|155|39|24|26|11|25.332|25.33|3.79
7|Truncus costocervicalis sinister|90|10|-|11|5|12.102|10.50|2.34
8|A subclavia sinistra 2|155|19|13|24|8|24.11|24.11|3.68
9|A cervicalis profunda sinistra|115|70|-|3|1|2.82|2.82|0.87
10|A subclavia sinistra 3|155|14|8|24|8|24.11|24.11|3.68
11|A vertebralis sinistra|135|95|-|12|5|14.17|9.98|2.45
12|A subclavia sinistra 4|240|40|6|23|6|22.89|22.89|3.57
13|A thoracica interna sinistra|280|137|-|12|4|12.11|12.11|2.44
14|A subclavia sinistra 5|240|7|8|23|6|22.89|22.89|3.57
15|A cervicalis superficialis sinistra|180|80|-|8|2|10.31|4.79|1.90
16|A axillaris sinistra 1|310|62|25|21|6|21.50|20.37|3.38
17|A suprascapularis sinistra|70|15|-|6|0|7.68|3.52|1.59
18|A axillaris sinistra 2|310|58|45|20|8|19.90|19.90|3.28
19|A subscapularis sinistra|10|10|-|17|7|16.80|16.80|2.96
20|A axillaris sinistra 3|310|23|18|18|5|18.02|18.02|3.09
21|A circumflexa humeri cranialis sinistra|230|30|-|5|2|6.11|2.79|1.39
22|A axillaris sinistra 4|270|70|28|17|3|17.05|17.05|2.99
23|A profunda brachii sinistra|325|5|-|11|5|11.281|9.60|2.23
24|A axillaris sinistra 5|270|82|11|14|1|15.35|12.79|2.67
25|A collateralis ulnaris sinistra|320|5|-|6|2|8.60|4.92|1.75
26|A mediana sinistra|270|145|-|7|3|10.01|5.30|1.90
27|Truncus brachiocephalicus 2|160|50|-|39|-|38.88|38.88|4.90
28|Truncus costocervicalis dexter|90|10|-|11|6|14.38|7.07|2.34
29|Truncus brachiocephalicus 3|160|10|-|39|-|38.88|38.88|4.90
30|A cervicalis profunda dextra|115|70|-|3|2|2.81|2.81|0.87
31|Truncus brachiocephalicus 4|160|10|-|39|-|38.88|38.88|4.90
32|A vertebralis dextra|135|95|-|12|5|16.95|7.12|2.54
33|Truncus brachiocephalicus 5|160|20|-|26|-|26.96|25.00|4.24
34|A subclavia dextra 1|240|30|-|26|11|25.00|25.00|3.76
35|A thoracica interna dextra|280|137|-|11|5|12.12|12.10|2.44
36|A cervicalis superficialis dextra|180|80|-|3|1|8.07|8.02|1.90
37|A axillaris dextra 1|310|62|25|21|6|20.95|20.94|3.38
38|A suprascapularis dextra|70|15|-|6|0|6.43|5.47|1.59
39|A axillaris dextra 2|310|58|45|20|8|19.90|19.90|3.28
40|A subscapularis dextra|10|10|-|17|7|16.80|16.80|2.96
41|A axillaris dextra 3|310|23|18|18|5|18.02|18.02|3.09
42|A circumflexa humeri cranialis dextra|230|30|-|5|2|6.115|2.79|1.39
43|A axillaris dextra 4|270|70|28|17|3|17.05|17.05|2.99
44|A profunda brachii dextra|325|5|-|11|5|10.47|10.47|2.23
45|A axillaris dextra 5|270|82|11|14|1|17.05|10.42|2.67
46|A collateralis ulnaris dextra|320|5|-|6|2|8.60|4.92|1.75
47|A mediana dextra|270|145|-|7|3|10.00|5.30|1.90
48|Truncus bicaroticus|165|78|91|22|19|22.06|21.26|3.45
49|A carotis communis sinistra|110|710|59|12|1|13.45|10.35|2.42
50|A carotis interna sinistra|90|120|-|4|1|4.43|3.53|1.25
51|A occipitalis sinistra|60|45|-|5|2|4.94|4.13|1.35
52|A carotis externa sinistra 1|130|65|41|10|3|10.04|10.04|2.18
53|Truncus linguofacialis sinister|180|80|-|6|3|6.54|5.50|1.60
54|A carotis externa sinistra 2|90|41|11|9|2|9.22|8.83|2.04
55|Ramus massetericus sinister|255|20|-|2|1|2.51|1.21|0.82
56|A carotis externa sinistra 3|90|13|3|9|2|8.56|8.55|1.98
57|A auricularis caudalis sinistra|55|10|-|3|2|3.953|1.74|1.07
58|A carotis externa sinistra 4|90|23|3|7|3|8.56|5.15|1.76
59|A temporalis superficialis sinistra|60|20|-|2|2|3.44|2.48|1.05
58b|A carotis externa sinistra 5|90|50|-|5|-|5.15|5.15|1.46
60|A carotis communis dextra|110|710|59|12|1|13.45|10.35|2.42
61|A carotis interna dextra|90|120|-|4|1|4.43|3.53|1.25
62|A occipitalis dextra|60|45|-|5|2|4.94|4.13|1.35
63|A carotis externa dextra 1|130|65|41|10|3|10.04|10.04|2.18
64|Truncus linguofacialis dexter|180|80|-|6|3|6.54|5.50|1.60
65|A carotis externa dextra 2|90|41|11|9|2|9.22|8.83|2.04
66|Ramus massetericus dexter|255|20|-|2|1|2.51|1.21|0.82
67|A carotis externa dextra 3|90|13|3|9|2|8.56|8.55|1.98
68|A auricularis caudalis dextra|55|10|-|3|2|3.95|1.74|1.07
69|A carotis externa dextra 4|90|23|3|7|3|8.56|5.15|1.76
70|A temporalis superficialis dextra|60|20|-|2|2|3.44|2.48|1.05
69b|A carotis externa dextra 5|90|50|-|5|-|5.15|5.15|1.46
71|Arcus aortae (lig. art. Botalli)|45|77|26|54|10|58.07|49.53|5.97
72|Aorta descendens 1|45|105|5|45|11|48.21|40.62|5.32
73|A broncho-oesophagea|270|66|-|11|2|13.71|6.31|2.26
74|Aorta descendens 2|0|486|69|36|1|38.44|32.28|4.64
75|A coeliaca|270|20|-|15|3|19.31|9.24|2.78
76|Aorta descendens 3|0|48|26|29|6|28.70|28.70|4.09
77|A mesenterica cranialis|270|20|-|11|7|13.48|7.56|2.29
78|Aorta descendens 4|0|30|35|29|10|28.70|28.70|4.09
79|A renalis dextra|270|30|-|11|2|13.26|7.21|2.26
80|Aorta descendens 5|0|20|19|29|5|28.70|28.70|4.09
81|A renalis sinistra|270|30|-|11|2|13.26|7.21|2.26
82|Aorta descendens 6|0|104|60|29|6|28.70|28.70|4.09
83|A ovarica sinistra|270|300|-|3|1|2.76|2.76|1.00
84|A ovarica dextra|270|300|-|3|1|2.76|2.76|1.00
85|Aorta descendens 7|0|40|27|29|6|28.70|28.70|4.09
86|A mesenterica caudalis|270|10|-|8|3|9.78|4.63|1.85
87|Aorta descendens 8|0|63|12|29|6|28.70|28.70|4.09
88|A iliaca interna sinistra|330|30|10|18|6|20.19|15.12|0.92
89|A iliaca externa sinistra 1|315|30|-|17|2|16.93|16.24|0.88
90|A circumflexa ilium profunda sinistra|240|160|-|6|2|7.58|3.66|0.48
91|A iliaca externa sinistra 2|280|29|19|16|3|15.99|15.54|0.86
92|A uterina sinistra|260|200|-|3|2|3.19|3.19|0.33
93|A iliaca externa sinistra 3|280|230|54|15|3|15.30|15.30|0.84
94|A profunda femoris sinistra|335|30|-|8|2|7.93|7.23|0.55
95|A femoralis sinistra 1|280|51|14|15|3|15.26|14.27|0.82
96|A circumflexa femoris lateralis sinistra|240|30|-|6|3|7.69|3.62|0.48
97|A femoralis sinistra 2|280|180|56|11|1|10.78|10.78|0.68
98|A saphena sinistra|285|625|-|3|3|2.59|2.59|0.29
99|A femoralis sinistra 3|280|25|26|10|1|10.78|9.71|0.66
100|A genus descendens sinistra|260|25|-|3|1|4.46|3.47|0.38
99b|A femoralis sinistra 4|280|50|-|10|-|9.71|9.71|0.64
101|A iliaca interna dextra|330|30|10|18|6|20.19|15.12|0.92
102|A iliaca externa dextra 1|315|30|-|17|2|16.98|16.19|0.88
103|A uterina dextra|260|200|-|6|2|3.19|3.19|0.33
104|A iliaca externa dextra 2|280|29|19|16|3|15.97|15.56|0.86
105|A circumflexa ilium profunda dextra|240|160|-|3|2|7.52|3.77|0.48
106|A iliaca externa dextra 3|280|230|54|15|3|15.30|15.30|0.84
107|A profunda femoris dextra|335|30|-|8|2|7.93|7.23|0.55
108|A femoralis dextra 1|280|51|14|15|3|15.26|14.27|0.82
109|A circumflexa femoris lateralis dextra|240|30|-|6|3|7.69|3.62|0.48
110|A femoralis dextra 2|280|180|56|11|1|10.78|10.78|0.68
111|A saphena dextra|285|625|-|3|3|2.59|2.59|0.29
112|A femoralis dextra 3|280|25|26|10|1|10.78|9.71|0.66
113|A genus descendens dextra|260|25|-|3|1|4.46|3.47|0.38
112b|A femoralis dextra 4|280|50|-|10|-|9.71|9.71|0.64
"""
# Note on 58b, 69b, 99b, 112b: the paper adds these unmeasured terminal segments
# "with an artificial length of 5 cm"; Table 1 prints 5 in its mm column, so we use 50 mm.


def _parse():
    segs = {}
    for line in _TABLE1.strip().splitlines():
        f = [s.strip() for s in line.split("|")]
        segs[f[0]] = dict(
            name=f[1], angle_deg=float(f[2]), length_mm=float(f[3]),
            d_prox_mm=float(f[7]), d_dist_mm=float(f[8]), distensibility_per_mmHg=float(f[9]) * 1e-3,
        )
    return segs


SEGMENTS = _parse()

# Which segments each segment feeds (read from Fig 1 and equine anatomy).
CHILDREN = {
    "1": ["2", "3", "4"],          # aortic root: coronaries and ascending aorta
    "4": ["5", "71"],              # brachiocephalic trunk and aortic arch
    "5": ["6", "27"],
    "6": ["7", "8"], "8": ["9", "10"], "10": ["11", "12"], "12": ["13", "14"],
    "14": ["15", "16"], "16": ["17", "18"], "18": ["19", "20"], "20": ["21", "22"],
    "22": ["23", "24"], "24": ["25", "26"],                      # left fore limb
    "27": ["28", "29"], "29": ["30", "31"], "31": ["32", "33"],
    "33": ["34", "48"],            # right subclavian and bicarotid trunk
    "34": ["35", "36", "37"],
    "37": ["38", "39"], "39": ["40", "41"], "41": ["42", "43"], "43": ["44", "45"],
    "45": ["46", "47"],                                          # right fore limb
    "48": ["49", "60"],            # left and right common carotid
    "49": ["50", "51", "52"],      # equine carotid ends in three branches
    "52": ["53", "54"], "54": ["55", "56"], "56": ["57", "58"], "58": ["59", "58b"],
    "60": ["61", "62", "63"],
    "63": ["64", "65"], "65": ["66", "67"], "67": ["68", "69"], "69": ["70", "69b"],
    "71": ["72"],
    "72": ["73", "74"], "74": ["75", "76"], "76": ["77", "78"], "78": ["79", "80"],
    "80": ["81", "82"], "82": ["83", "84", "85"], "85": ["86", "87"],
    "87": ["88", "89", "101", "102"],   # aortic quadrifurcation
    "89": ["90", "91"], "91": ["92", "93"], "93": ["94", "95"], "95": ["96", "97"],
    "97": ["98", "99"], "99": ["100", "99b"],                    # left hind limb
    "102": ["103", "104"], "104": ["105", "106"], "106": ["107", "108"],
    "108": ["109", "110"], "110": ["111", "112"], "112": ["113", "112b"],  # right hind limb
}

ROOT = "1"

# Body region of each terminal branch, for comparing the cardiac-output
# distribution with the paper's Table 2. The paper does not list its grouping.
# This one is anatomical and, among the plausible groupings we tried, it best
# reproduces the paper's no-gravity column with the S1 resistances.
REGIONS = {
    "heart": ["2", "3"],                                   # coronaries
    "brain": ["50", "61", "11", "32"],                     # internal carotids, vertebrals
    "muscle": ["17", "19", "21", "23", "25", "26", "38", "40", "42", "44", "46", "47",
               "94", "96", "98", "100", "99b", "107", "109", "111", "113", "112b"],  # limbs
    "kidney": ["79", "81"],
    "splanchnic": ["75", "77", "86", "73", "88", "101"],   # gut, oesophagus, pelvic viscera
    "other": ["7", "9", "13", "15", "28", "30", "35", "36", "51", "62",
              "53", "55", "57", "59", "58b", "64", "66", "68", "70", "69b",
              "83", "84", "90", "105", "92", "103"],
}

# Locations reported in the paper's Tables 3 and 4.
LOCATIONS = {"Prox Ao": "1", "Dist Ao": "87", "CCA": "49", "MA": "26", "EIA": "93"}

# The aorta from the root to the quadrifurcation, used for pulse wave velocity
# and for the pressures along the aorta in Fig 5.
AORTA_PATH = ["1", "4", "71", "72", "74", "76", "78", "80", "82", "85", "87"]


def parent_of():
    return {c: p for p, kids in CHILDREN.items() for c in kids}


def terminals():
    return [s for s in SEGMENTS if s not in CHILDREN]


def check_tree():
    """Every segment but the root has exactly one parent; terminals match the paper."""
    kids = [c for v in CHILDREN.values() for c in v]
    assert len(kids) == len(set(kids)), "a segment has two parents"
    assert set(kids) | {ROOT} == set(SEGMENTS), set(SEGMENTS) ^ (set(kids) | {ROOT})
    assert len(SEGMENTS) == 117 and len(terminals()) == 62
    assigned = [s for v in REGIONS.values() for s in v]
    assert sorted(assigned) == sorted(terminals()), set(assigned) ^ set(terminals())
    return True
