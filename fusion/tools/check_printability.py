"""Швидка перевірка STL для друку: об'єм, габарит, замкнутість сітки, площа контакту зі столом,
площа нависань більше 45 градусів і горизонтальних «мостів».
Запуск: python check_printability.py ../output/Case_Base_print.stl ../output/Case_Lid_print_flipped.stl
Потрібні пакети: trimesh, numpy (pip install trimesh numpy)."""
import sys, collections
import numpy as np
import trimesh

for path in sys.argv[1:]:
    m = trimesh.load(path)
    z0 = m.bounds[0][2]
    n, a, zc = m.face_normals, m.area_faces, m.triangles_center[:, 2]
    on_bed = (n[:, 2] < -0.99) & (zc < z0 + 0.05)
    steep = (n[:, 2] < -0.71) & (zc > z0 + 0.3)
    flat = (n[:, 2] < -0.99) & (zc > z0 + 0.3)
    ceilings = collections.defaultdict(float)
    for z, s in zip(zc[flat], a[flat]):
        ceilings[round(float(z), 1)] += s
    print(path)
    print('  габарит, мм:', (m.bounds[1] - m.bounds[0]).round(1).tolist(), ' об\'єм, см3:', round(m.volume / 1000, 1),
          ' замкнута сітка:', m.is_watertight)
    print('  контакт зі столом, мм2:', round(a[on_bed].sum()), ' нависання > 45°, мм2:', round(a[steep].sum()))
    print('  горизонтальні стелі (висота: площа мм2):', sorted((k, round(v)) for k, v in ceilings.items() if v > 15))
