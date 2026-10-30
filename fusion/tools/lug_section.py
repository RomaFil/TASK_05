# Розріз кутової колони через вісь (fusion/images/lug_detail.png) зі STL: python fusion/tools/lug_section.py
# Потрібні trimesh, numpy, matplotlib, shapely, rtree. Координати колони (X0, Y0) і ZLT взято зі скрипта корпусу.
import numpy as np, trimesh
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
R = r'C:\Users\Roman_\Documents\GitHub\TASK_05\fusion'
base = trimesh.load(R + r'\output\Case_Base_print.stl')
lid = trimesh.load(R + r'\output\Case_Lid_print_flipped.stl')
X0, Y0, ZLT = -23.8, -5.2, 27.5
def polys(mesh, flip):
    sec = mesh.section(plane_origin=[X0, 0, 0], plane_normal=[1, 0, 0])
    if flip:   # кришка надрукована догори дном: y' = -y, z' = ZLT - z
        M = np.array([[0, -1, 0, 0], [0, 0, -1, ZLT], [1, 0, 0, -X0], [0, 0, 0, 1.]])
    else:
        M = np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, -X0], [0, 0, 0, 1.]])
    p2, _ = sec.to_2D(to_2D=M)
    return p2.polygons_full
fig, ax = plt.subplots(figsize=(5.5, 9), dpi=130)
def draw(pg, color):
    for g in pg:
        verts = list(g.exterior.coords); codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 1)
        for r in g.interiors:
            v = list(r.coords); verts += v; codes += [Path.MOVETO] + [Path.LINETO] * (len(v) - 1)
        ax.add_patch(PathPatch(Path(verts, codes), fc=color, ec='k', lw=0.6))
draw(polys(base, False), '#7aa6d6'); draw(polys(lid, True), '#f0a868')
ax.set_xlim(Y0 - 8, Y0 + 8); ax.set_ylim(-21, 29); ax.set_aspect('equal'); ax.grid(alpha=.3)
ax.axvline(Y0, color='r', lw=.6, ls='--')
ax.set_xlabel('y, мм (вісь колони червона)'); ax.set_ylabel('z, мм')
ax.set_title('Кутова колона, розріз через вісь:\nосновa (синє) і кришка (помаранчеве)', fontsize=10)
fig.tight_layout(); fig.savefig(R + r'\images\lug_detail.png'); print('ok')

