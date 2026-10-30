# -*- coding: utf-8 -*-
# Корпус Motion Logger v5 (30.10.2026): правки після друку v4.
#  - кришка кріпиться до основи сама: 4 колони M3 на зовнішніх кутах, гвинт згори, гайка M3 вкладається в боковий паз
#    основи (не вплавляється), тож корпус закривається й без плати; труби під гвинти й світловоди в кришці прибрано;
#  - напису нема, верх кришки плоский; ніші кнопок наскрізні з полицею 45 градусів замість стелі;
#  - вентиляція стінок ромбами (45 градусів, без мостів, перемички 2.5 мм); вікна USB/Ethernet з плоским верхом
#    і товстою перемичкою над ними; вікно microSD ширше й доходить до лівої стінки.
# Усі розміри в мм. Система координат P: лівий нижній кут Pi 5 = (0;0), Z=0 = верх плати Motion Logger, Z вгору.
# Зв'язок з Altium (пін 1 J1 = початок): P = Altium + (8.37; 51.23).
# Друк без підтримок, крім трьох вікон правої стінки (плоский верх 15-16 мм): край біля столу має фаску не гостріше
# 45 градусів, решта вікон з гострим дахом 45 градусів, гнізда гвинтів кришки закінчуються конусом, а не стелею.
import adsk.core, adsk.fusion, traceback, math, os

# ---------------- ПАРАМЕТРИ ----------------
H = 11.0
CAV = 20.0
W = 3.0
FL = 3.0
LT = 7.5
POST_H = 3.0
POST_D = 7.0
HOLE_D = 2.9
CB_D = 5.6
CB_DEP = 1.8
TONGUE = 1.2
SKIRT = 1.5
STEP_Z = 11.0
TONGUE_H = 2.0
GAP_LID = 0.2
PLATE_T = 1.5
PX0, PX1, PY0, PY1 = -19.80, 65.20, -0.77, 60.00
CAVX0, CAVX1, CAVY0, CAVY1 = -20.8, 88.6, -2.2, 60.8
R_OUT = 5.0         # радіус вертикальних кутів (v3: 3)
EDGE_CH = 3.0       # фаска 45 градусів на ребрі біля столу (основа знизу, кришка зверху)
EDGE_FR = 4.0       # згладження переходу стінка-фаска (має бути менше R_OUT)
try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
OUT_DIR = os.path.normpath(os.path.join(_HERE, "..", "output"))
IN_DIR = os.path.normpath(os.path.join(_HERE, "..", "inputs"))
IMG_DIR = os.path.normpath(os.path.join(_HERE, "..", "images"))

HOLES = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]
LEDS = [(49.01, 19.48), (49.01, 11.86), (49.01, 4.24)]
LED_WIN = 5.5
GPS = (0.81, 35.43, 38.5, 26.5)
PLATE_HOLES = [(3.5, 3.5, 2.7), (61.5, 3.5, 2.7), (3.5, 52.5, 2.7), (61.5, 52.5, 2.7),
               (-14.49, 45.03, 3.2), (-14.49, 25.83, 3.2), (16.71, 45.03, 3.2), (16.71, 25.83, 3.2)]
BTN = [(-10.5, 9.0), (19.0, 9.0)]
POCKET = (15.5, 19.5)
POCKET_DEP = 5.5
POCKET_LEDGE = 1.5  # полиця 45 градусів на дні ніші, далі ніша наскрізна (модуль кнопки лежить краями на полиці)
SLOT = (12.0, 4.5)
SUPPORTS = [(-17.0, 6.0), (-17.0, 54.0)]
SUP_D = 6.0
SD_X1, SD_Y0, SD_Y1 = 13.0, 18.0, 38.0   # вікно microSD у дні: від лівої стінки (з вирізом у ній) до x = 13

# кріплення кришки: колони на 4 зовнішніх кутах, гвинт M3 згори, гайка M3 у пазу основи
LUG_D = 10.0        # діаметр колони, центр колони = кут габариту корпусу
LUG_HOLE = 3.4      # отвір під M3 (друк звужує ~0.2)
LUG_HEAD_D = 6.2    # гніздо під головку гвинта в кришці
LUG_SEAT_Z = 20.0   # верх конуса-упору головки (конус 45 градусів замість стелі: друкується без мосту)
LUG_CH_LID = 1.0    # фаска колони біля верху кришки (більша прорізала б гніздо головки)
NUT_AF, NUT_H = 5.8, 2.8   # паз гайки M3 (5.5 під ключ, 2.4 товщина) із зазором
NUT_TOP = 6.0       # стеля паза гайки
LUG_TIP = -3.0      # дно глухого отвору під кінчик гвинта

# соти на кришці: a = радіус описаного кола шестикутника (сторона), T = товщина перемичок
HEX_A_LID, HEX_T = 3.5, 1.6
# ромби на стінках: діагональ і перемичка
VENT_D, VENT_T = 8.0, 2.5

MM = 0.1
LOG = []
def log(s): LOG.append(str(s))

def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        build(app, ui)
    except:
        log(traceback.format_exc())
        ui.messageBox('Помилка скрипта:\n' + traceback.format_exc())
    finally:
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(os.path.join(OUT_DIR, 'script_log.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(LOG))

def P(x, y, z): return adsk.core.Point3D.create(x * MM, y * MM, z * MM)
def V(x, y, z): return adsk.core.Vector3D.create(x, y, z)

def build(app, ui):
    bm = adsk.fusion.TemporaryBRepManager.get()
    zpt = -PLATE_T - H
    zlt = CAV + LT

    app.preferences.generalPreferences.defaultModelingOrientation = adsk.core.DefaultModelingOrientations.ZUpModelingOrientation
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.DirectDesignType
    root = design.rootComponent
    log('units=' + design.unitsManager.defaultLengthUnits)

    def box(x0, y0, z0, x1, y1, z1):
        c = P((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
        return bm.createBox(adsk.core.OrientedBoundingBox3D.create(c, V(1, 0, 0), V(0, 1, 0), (x1 - x0) * MM, (y1 - y0) * MM, (z1 - z0) * MM))
    def cyl(x, y, z0, z1, d): return bm.createCylinderOrCone(P(x, y, z0), d / 2 * MM, P(x, y, z1), d / 2 * MM)
    def cone(x, y, z0, d0, z1, d1): return bm.createCylinderOrCone(P(x, y, z0), d0 / 2 * MM, P(x, y, z1), d1 / 2 * MM)
    def uni(a, b): bm.booleanOperation(a, b, adsk.fusion.BooleanTypes.UnionBooleanType); return a
    def dif(a, b): bm.booleanOperation(a, b, adsk.fusion.BooleanTypes.DifferenceBooleanType); return a
    def rrect(x0, y0, x1, y1, z0, z1, r):
        b = box(x0 + r, y0, z0, x1 - r, y1, z1)
        uni(b, box(x0, y0 + r, z0, x1, y1 - r, z1))
        for (cx, cy) in ((x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)):
            uni(b, cyl(cx, cy, z0, z1, 2 * r))
        return b
    ROOF_FLAT = 6.0
    SQ = math.sqrt(0.5)
    def roof(axis, a0, a1, b0, b1, zt, flat=ROOF_FLAT):
        # flat = ширина плоского верху (міст); 0 = гострий дах, друкується без підтримок
        w = b1 - b0
        sd = w / math.sqrt(2)
        if axis == 'x':
            c = P((a0 + a1) / 2, (b0 + b1) / 2, zt)
            d = bm.createBox(adsk.core.OrientedBoundingBox3D.create(c, V(1, 0, 0), V(0, SQ, SQ), (a1 - a0) * MM, sd * MM, sd * MM))
            if flat > 0:
                dif(d, box(a0 - 1, b0 - 1, zt + (w - flat) / 2, a1 + 1, b1 + 1, zt + w))
        else:
            c = P((b0 + b1) / 2, (a0 + a1) / 2, zt)
            d = bm.createBox(adsk.core.OrientedBoundingBox3D.create(c, V(0, 1, 0), V(SQ, 0, SQ), (a1 - a0) * MM, sd * MM, sd * MM))
            if flat > 0:
                dif(d, box(b0 - 1, a0 - 1, zt + (w - flat) / 2, b1 + 1, a1 + 1, zt + w))
        return d
    def frustum_down(cx, cy, z0, wx, wy):
        # переріз wx x wy на висоті z0, звужується вниз під 45 градусів (перетин двох дахів)
        a = bm.createBox(adsk.core.OrientedBoundingBox3D.create(P(cx, cy, z0), V(1, 0, 0), V(0, SQ, SQ), (wx + 2) * MM, wy * SQ * MM, wy * SQ * MM))
        b = bm.createBox(adsk.core.OrientedBoundingBox3D.create(P(cx, cy, z0), V(0, 1, 0), V(SQ, 0, SQ), (wy + 2) * MM, wx * SQ * MM, wx * SQ * MM))
        bm.booleanOperation(a, b, adsk.fusion.BooleanTypes.IntersectionBooleanType)
        return a
    def newcomp(name):
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = name
        return occ
    def addbody(occ, body, name):
        bd = occ.component.bRepBodies.add(body)
        bd.name = name
        return bd

    # ---------- заготовка з м'яким ребром (фаска 45 + згладження) біля столу ----------
    ROUND_OK = []
    def soft_blank(x0, y0, x1, y1, z0, z1, r, end):
        plain = rrect(x0, y0, x1, y1, z0, z1, r)
        occ = None
        try:
            occ = newcomp('tmp_blank')
            bd = addbody(occ, rrect(x0, y0, x1, y1, z0, z1, r), 'b')
            zc = (z0 if end == 'bottom' else z1) * MM
            face = None
            for f in bd.faces:
                if f.geometry.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType:
                    continue
                bb = f.boundingBox
                if abs(bb.minPoint.z - zc) < 1e-4 and abs(bb.maxPoint.z - zc) < 1e-4:
                    face = f
            edges = adsk.core.ObjectCollection.create()
            for e in face.edges:
                edges.add(e)
            chs = occ.component.features.chamferFeatures
            ci = chs.createInput2()
            ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges, adsk.core.ValueInput.createByReal(EDGE_CH * MM), True)
            chs.add(ci)
            bd = occ.component.bRepBodies.item(0)
            zl = (z0 + EDGE_CH if end == 'bottom' else z1 - EDGE_CH) * MM
            edges2 = adsk.core.ObjectCollection.create()
            for e in bd.edges:
                bb = e.boundingBox
                if abs(bb.minPoint.z - zl) < 1e-4 and abs(bb.maxPoint.z - zl) < 1e-4:
                    edges2.add(e)
            log('soft_blank %s: loop edges %d' % (end, edges2.count))
            fls = occ.component.features.filletFeatures
            fi = fls.createInput()
            fi.addConstantRadiusEdgeSet(edges2, adsk.core.ValueInput.createByReal(EDGE_FR * MM), True)
            fls.add(fi)
            res = bm.copy(occ.component.bRepBodies.item(0))
            occ.deleteMe()
            ROUND_OK.append(end)
            return res
        except:
            log('SOFT EDGE FAILED (%s): %s' % (end, traceback.format_exc()))
            try:
                if occ is not None:
                    occ.deleteMe()
            except:
                pass
            return plain

    # ---------- соти ----------
    def hexcut(cx, cy, cz, u, v, a, length):
        res = None
        s3 = math.sqrt(3)
        for ang in (90, 30, 150):
            r = math.radians(ang)
            p = [u[i] * math.cos(r) + v[i] * math.sin(r) for i in range(3)]
            d = [-u[i] * math.sin(r) + v[i] * math.cos(r) for i in range(3)]
            b = bm.createBox(adsk.core.OrientedBoundingBox3D.create(P(cx, cy, cz), V(*d), V(*p), 3.2 * a * MM, s3 * a * MM, length * MM))
            if res is None:
                res = b
            else:
                bm.booleanOperation(res, b, adsk.fusion.BooleanTypes.IntersectionBooleanType)
        return res
    # ---------- ромби (квадрат, повернутий на 45 градусів у площині u-v): гострі верх і низ, мостів нема ----------
    def diamond_cut(cx, cy, cz, u, v, d, length):
        a = [(u[i] + v[i]) * SQ for i in range(3)]
        b = [(v[i] - u[i]) * SQ for i in range(3)]
        return bm.createBox(adsk.core.OrientedBoundingBox3D.create(P(cx, cy, cz), V(*a), V(*b), d * SQ * MM, d * SQ * MM, length * MM))
    def diamond_grid(umin, umax, vmin, vmax, d, t, skip=None):
        # сусіди по діагоналі зсунуті на (q; q): відстань між паралельними гранями = t
        h = d / 2
        q = h + t * SQ
        uc, vc = (umin + umax) / 2, (vmin + vmax) / 2
        out = []
        for k in range(-20, 21):
            v = vc + k * q
            if v - h < vmin - 1e-9 or v + h > vmax + 1e-9:
                continue
            for m in range(-40, 41):
                u = uc + m * q
                if (m + k) % 2 or u - h < umin - 1e-9 or u + h > umax + 1e-9:
                    continue
                if skip is None or not skip(u, v):
                    out.append((u, v))
        return out
    def hex_grid(umin, umax, vmin, vmax, a, t):
        ap = a + t / math.sqrt(3)
        dx, dy, apo = 1.5 * ap, math.sqrt(3) * ap, math.sqrt(3) / 2 * a
        ncol = int((umax - umin - 2 * a) // dx) + 1
        if ncol < 1:
            return []
        u0 = (umin + umax) / 2 - (ncol - 1) * dx / 2
        vc = (vmin + vmax) / 2
        out = []
        for j in range(ncol):
            off = 0.0 if j % 2 == 0 else 0.5
            for k in range(-20, 21):
                v = vc + (k + off) * dy
                if v - apo >= vmin - 1e-9 and v + apo <= vmax + 1e-9:
                    out.append((u0 + j * dx, v))
        return out

    # ---------- Z-рівні ----------
    dz = zpt - 1.31
    pi_bot = 0.03 + dz
    zft = pi_bot - POST_H
    zfb = zft - FL
    log('H=%s zpt=%.2f dz=%.2f pi_bot=%.2f floor top=%.2f bottom=%.2f' % (H, zpt, dz, pi_bot, zft, zfb))
    zlb = STEP_Z + GAP_LID

    # ---------- плата Motion Logger (проста модель) і Pi ----------
    im = app.importManager
    def imp(fname, shift):
        before = set(o.name for o in root.occurrences)
        opts = im.createSTEPImportOptions(os.path.join(IN_DIR, fname))
        im.importToTarget(opts, root)
        new = [o for o in root.occurrences if o.name not in before]
        for o in new:
            m = adsk.core.Matrix3D.create()
            m.translation = V(shift[0] * MM, shift[1] * MM, shift[2] * MM)
            o.transform2 = m
        return new
    # Pi імпортуємо й зсуваємо ПІСЛЯ скруглень: фаска/згладження пишуть історію, і вона скидала зсув occurrence
    plate_b = rrect(PX0, PY0, PX1, PY1, -PLATE_T, 0, 2.0)
    for (x, y, d) in PLATE_HOLES:
        dif(plate_b, cyl(x, y, -PLATE_T - 1, 1, d))
    occ_plate = newcomp('Plate_Motion_Logger')
    addbody(occ_plate, plate_b, 'Plate')
    # ---------- ОСНОВА ----------
    OX0, OX1, OY0, OY1 = CAVX0 - W, CAVX1 + W, CAVY0 - W, CAVY1 + W
    ztong = STEP_Z + TONGUE_H
    # колони кріплення кришки: центр у куті габариту, виступають назовні; (x, y, напрям назовні по x, по y)
    LUGS = [(OX0, OY0, -1, -1), (OX1, OY0, 1, -1), (OX0, OY1, -1, 1), (OX1, OY1, 1, 1)]
    base = soft_blank(OX0, OY0, OX1, OY1, zfb, STEP_Z, R_OUT, 'bottom')
    uni(base, rrect(CAVX0 - TONGUE, CAVY0 - TONGUE, CAVX1 + TONGUE, CAVY1 + TONGUE, STEP_Z - 0.1, ztong, R_OUT - (W - TONGUE)))
    for (cx, cy, sx, sy) in LUGS:
        uni(base, cone(cx, cy, zfb, LUG_D - 2 * EDGE_CH, zfb + EDGE_CH, LUG_D))     # фаска 45 біля столу, як у корпусу
        uni(base, cyl(cx, cy, zfb + EDGE_CH - 0.05, STEP_Z, LUG_D))
    dif(base, rrect(CAVX0, CAVY0, CAVX1, CAVY1, zft, ztong + 1, R_OUT - W))
    for (x, y) in SUPPORTS:
        uni(base, cyl(x, y, zft - 0.1, -PLATE_T - 0.3, SUP_D))
    for (x, y) in HOLES:
        uni(base, cyl(x, y, zft - 0.1, pi_bot, POST_D))
    for (x, y) in HOLES:
        dif(base, cyl(x, y, zfb - 1, pi_bot + 0.1, HOLE_D))
        dif(base, cyl(x, y, zfb - 1, zfb + CB_DEP, CB_D))
    # вікна правої стінки: розмір як у v4, але верх плоский (v4: дах 45 градусів лишав над вікном USB лише 1.7 мм і він
    # відламався); тепер перемичка до верху основи 6.5 мм над USB і 9.4 мм над Ethernet, підтримка лише всередині вікна
    zt_usb = 17.53 + dz + 0.8
    zb_eth = -0.66 + dz - 0.8
    zt_eth = 14.64 + dz + 0.8
    xr0, xr1 = CAVX1 - 0.5, OX1 + 1
    for (y0, y1, zb, zt) in ((2.28 - 0.5, 18.22 + 0.5, zb_eth, zt_eth),
                             (21.75 - 0.5, 36.25 + 0.5, zb_eth, zt_usb),
                             (39.75 - 0.5, 54.25 + 0.5, zb_eth, zt_usb)):
        dif(base, box(xr0, y0, zb, xr1, y1, zt))
    log('lintel over USB %.1f mm, over Ethernet %.1f mm' % (STEP_Z - zt_usb, STEP_Z - zt_eth))
    zb_b, zt_b = 0.24 + dz - 2.0, 4.68 + dz + 2.0
    for (x0, x1) in ((6.73 - 2.0, 15.67 + 2.0), (22.2 - 2.0, 29.4 + 2.0), (35.6 - 2.0, 42.8 + 2.0)):
        wnd = box(x0, OY0 - 1, zb_b, x1, CAVY0 + 0.5, zt_b)
        uni(wnd, roof('y', OY0 - 1, CAVY0 + 0.5, x0, x1, zt_b, 0))
        dif(base, wnd)
    # microSD знизу: вікно в дні від лівої стінки до x = SD_X1, у стінці виріз до дна з гострим дахом, щоб дістати пальцем
    dif(base, box(OX0 - 1, SD_Y0, zfb - 1, SD_X1, SD_Y1, zft + 0.1))
    sd_apex = zft + (SD_Y1 - SD_Y0) / 2
    wnd = box(OX0 - 1, SD_Y0, zfb - 1, CAVX0 + 0.5, SD_Y1, zft)
    uni(wnd, roof('x', OX0 - 1, CAVX0 + 0.5, SD_Y0, SD_Y1, zft, 0))
    dif(base, wnd)
    for k in range(-2, 3):                                                          # вентиляція під процесором
        dif(base, box(33.15 + 3.6 * k - 1.2, 22.75 - 9, zfb - 1, 33.15 + 3.6 * k + 1.2, 22.75 + 9, zft + 0.1))
    # ромби на задній (+y) і лівій (-x) стінках основи
    zlo, zhi = zft + 1.5, 9.5
    n_vent = 0
    ya, yb = CAVY1 - 0.3, OY1 + 1
    for (u, v) in diamond_grid(-15.0, 82.0, zlo, zhi, VENT_D, VENT_T):
        dif(base, diamond_cut(u, (ya + yb) / 2, v, (1, 0, 0), (0, 0, 1), VENT_D, yb - ya)); n_vent += 1
    xa, xb = OX0 - 1, CAVX0 + 0.3
    yc_sd = (SD_Y0 + SD_Y1) / 2
    # ромб не ближче за VENT_T до даху вирізу microSD: обидва мають грані 45 градусів, тож досить порівняти z + |y - yc|
    near_sd = lambda u, v: v + abs(u - yc_sd) - VENT_D / 2 < sd_apex + VENT_T * math.sqrt(2)
    for (u, v) in diamond_grid(OY0 + R_OUT + 3.0, OY1 - R_OUT - 3.0, zlo, zhi, VENT_D, VENT_T, near_sd):
        dif(base, diamond_cut((xa + xb) / 2, u, v, (0, 1, 0), (0, 0, 1), VENT_D, xb - xa)); n_vent += 1
    log('wall vents: %d' % n_vent)
    # отвори колон: гвинт M3 згори, гайка заходить у шестигранний паз збоку (назовні по діагоналі кута)
    for (cx, cy, sx, sy) in LUGS:
        dif(base, cyl(cx, cy, LUG_TIP, STEP_Z + 1, LUG_HOLE))
        s = (sx * SQ, sy * SQ, 0.0)
        n = (-sy * SQ, sx * SQ, 0.0)
        zc = NUT_TOP - NUT_H / 2
        dif(base, hexcut(cx, cy, zc, s, n, NUT_AF / math.sqrt(3), NUT_H))
        dif(base, bm.createBox(adsk.core.OrientedBoundingBox3D.create(
            P(cx + s[0] * LUG_D / 2, cy + s[1] * LUG_D / 2, zc), V(*s), V(*n), LUG_D * MM, NUT_AF * MM, NUT_H * MM)))
    seat = LUG_SEAT_Z - (LUG_HEAD_D - 5.5) / 2     # де ляже головка ⌀5.5
    log('lid screws M3: length %.1f..%.1f mm (head %.1f, nut top %.1f, hole bottom %.1f)' % (
        seat - NUT_TOP + 2.4 + 0.5, seat - LUG_TIP - 0.5, seat, NUT_TOP, LUG_TIP))
    occ_base = newcomp('Case_Base')
    bd_base = addbody(occ_base, base, 'Base')

    # ---------- КРИШКА ----------
    # верх плоский, без напису і без труб усередині: кришка тримається лише на 4 колонах і не торкається плати
    lid = soft_blank(OX0, OY0, OX1, OY1, zlb, zlt, R_OUT, 'top')
    for (cx, cy, sx, sy) in LUGS:
        uni(lid, cyl(cx, cy, zlb, zlt - LUG_CH_LID + 0.05, LUG_D))
        uni(lid, cone(cx, cy, zlt - LUG_CH_LID, LUG_D, zlt, LUG_D - 2 * LUG_CH_LID))
    # колони додано до вирізу під язик основи: так вони не заходять на язик у кутах
    dif(lid, rrect(CAVX0 - SKIRT, CAVY0 - SKIRT, CAVX1 + SKIRT, CAVY1 + SKIRT, zlb - 1, ztong, R_OUT - (W - SKIRT)))
    dif(lid, rrect(CAVX0, CAVY0, CAVX1, CAVY1, -0.5, CAV, R_OUT - W))
    for (x, y) in LEDS:
        dif(lid, cyl(x, y, CAV - 1, zlt + 1, LED_WIN))
    gx, gy, gw, gh = GPS
    dif(lid, box(gx - gw / 2, gy - gh / 2, CAV - 1, gx + gw / 2, gy + gh / 2, zlt + 1))
    # ніші кнопок: замість стелі (на друці кришка догори дном) полиця 45 градусів і наскрізний отвір
    zpk = zlt - POCKET_DEP
    for (bx, by) in BTN:
        pw, ph = POCKET
        e = POCKET_LEDGE
        dif(lid, box(bx - pw / 2, by - ph / 2, zpk, bx + pw / 2, by + ph / 2, zlt + 1))
        dif(lid, frustum_down(bx, by, zpk + 0.01, pw, ph))
        dif(lid, box(bx - pw / 2 + e, by - ph / 2 + e, CAV - 1, bx + pw / 2 - e, by + ph / 2 - e, zpk + 0.1))
        dif(lid, box(bx - SLOT[0] / 2, by - ph / 2, CAV - 1, bx + SLOT[0] / 2, by - ph / 2 + SLOT[1], zlt + 1))
    # соти на верху кришки (над правою частиною Pi): вихід гарячого повітря; отвори вертикальні, тож без підтримок
    n_lid = 0
    for (u, v) in hex_grid(66.8, 87.6, -1.0, 24.0, HEX_A_LID, HEX_T):
        dif(lid, hexcut(u, v, (CAV - 0.5 + zlt + 1) / 2, (1, 0, 0), (0, 1, 0), HEX_A_LID, zlt + 1 - (CAV - 0.5))); n_lid += 1
    log('lid hexes: %d' % n_lid)
    # гнізда гвинтів: головка в гнізді ⌀LUG_HEAD_D, під нею конус 45 градусів до отвору M3 (без стелі, що запечатувала отвір)
    for (cx, cy, sx, sy) in LUGS:
        dif(lid, cyl(cx, cy, zlb - 1, LUG_SEAT_Z, LUG_HOLE))
        dif(lid, cone(cx, cy, LUG_SEAT_Z - (LUG_HEAD_D - LUG_HOLE) / 2, LUG_HOLE, LUG_SEAT_Z + 0.01, LUG_HEAD_D))
        dif(lid, cyl(cx, cy, LUG_SEAT_Z, zlt + 1, LUG_HEAD_D))
    occ_lid = newcomp('Case_Lid')
    bd_lid = addbody(occ_lid, lid, 'Lid')

    # ---------- Pi 5 (проксі) на місці ----------
    pi = imp('pi5_proxy.step', (0, 0, dz))
    for o in pi: o.component.name = 'Pi5_proxy'
    log('imported pi %d' % len(pi))

    # ---------- кришка догори дном для друку ----------
    occ_pr = None
    try:
        cp = bm.copy(lid)
        m = adsk.core.Matrix3D.create()
        m.setToRotation(math.pi, V(1, 0, 0), P(0, 0, 0))
        m.translation = V(0, 0, zlt * MM)
        bm.transform(cp, m)
        occ_pr = newcomp('Case_Lid_for_print')
        addbody(occ_pr, cp, 'Lid_flipped')
        occ_pr.isLightBulbOn = False
    except:
        log('flip failed: ' + traceback.format_exc())

    log('rounded ends ok: %s' % ROUND_OK)
    log('volume base %.2f cm3, lid %.2f cm3' % (bd_base.volume, bd_lid.volume))

    # ---------- перевірка перетинів ----------
    try:
        for o in root.occurrences:
            bb = o.boundingBox
            log('occ %s world mm x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f children=%d' % (
                o.name, bb.minPoint.x * 10, bb.maxPoint.x * 10, bb.minPoint.y * 10, bb.maxPoint.y * 10,
                bb.minPoint.z * 10, bb.maxPoint.z * 10, o.childOccurrences.count))
    except:
        log('occ bbox failed: ' + traceback.format_exc())
    try:
        ents = adsk.core.ObjectCollection.create()
        for occ in root.allOccurrences:
            if occ.name.startswith('Case_Lid_for_print'):
                continue
            for bd in occ.bRepBodies:
                ents.add(bd)
        res = design.analyzeInterference(design.createInterferenceInput(ents))
        bad = 0
        for r in res:
            n1 = r.entityOne.parentComponent.name
            n2 = r.entityTwo.parentComponent.name
            if n1 == n2:
                continue
            if 'Case_' in n1 or 'Case_' in n2:
                bad += 1
                ib = r.interferenceBody.boundingBox
                b1 = r.entityOne.boundingBox
                b2 = r.entityTwo.boundingBox
                log('  INTERFERENCE %s <-> %s vol=%.4f cm3 at mm x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (
                    n1, n2, r.interferenceBody.volume, ib.minPoint.x * 10, ib.maxPoint.x * 10, ib.minPoint.y * 10,
                    ib.maxPoint.y * 10, ib.minPoint.z * 10, ib.maxPoint.z * 10))
                log('    one: %s z %.1f..%.1f   two: %s z %.1f..%.1f' % (
                    r.entityOne.name, b1.minPoint.z * 10, b1.maxPoint.z * 10, r.entityTwo.name, b2.minPoint.z * 10, b2.maxPoint.z * 10))
        log('interferences total %d, with case: %d' % (res.count, bad))
    except:
        log('interference check failed: ' + traceback.format_exc())

    # ---------- експорт ----------
    os.makedirs(OUT_DIR, exist_ok=True)
    em = design.exportManager
    try:
        o = em.createSTEPExportOptions(os.path.join(OUT_DIR, 'Motion_Logger_case_assembly.step'), root)
        em.execute(o)
        log('step ok')
    except:
        log('export step failed: ' + traceback.format_exc())
    for bd, fn in ((bd_base, 'Case_Base_print.stl'),
                   (occ_pr.component.bRepBodies.item(0), 'Case_Lid_print_flipped.stl')):
        try:
            o = em.createSTLExportOptions(bd, os.path.join(OUT_DIR, fn))
            o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
            o.sendToPrintUtility = False
            em.execute(o)
            log(fn + ' ok')
        except:
            log('stl failed ' + fn + ': ' + traceback.format_exc())

    # ---------- зображення моделі ----------
    try:
        img_dir = IMG_DIR
        os.makedirs(img_dir, exist_ok=True)
        vp = app.activeViewport
        cx, cy, cz = (OX0 + OX1) / 2, (OY0 + OY1) / 2, (zfb + zlt) / 2
        def shot(name, eye, up, ortho, show):
            for o in pi: o.isLightBulbOn = False
            occ_plate.isLightBulbOn = False
            occ_base.isLightBulbOn = 'base' in show
            occ_lid.isLightBulbOn = 'lid' in show
            if occ_pr is not None: occ_pr.isLightBulbOn = False
            cam = vp.camera
            cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType if ortho else adsk.core.CameraTypes.PerspectiveCameraType
            cam.eye = P(*eye); cam.target = P(cx, cy, cz); cam.upVector = V(*up)
            cam.isSmoothTransition = False
            vp.camera = cam
            vp.fit()
            vp.saveAsImageFile(os.path.join(img_dir, name), 1800, 1200)
            log('image ' + name)
        shot('case_isometric.png', (cx + 150, cy - 190, cz + 170), (0, 0, 1), False, ('base', 'lid'))
        shot('case_isometric_back.png', (cx - 170, cy + 180, cz + 150), (0, 0, 1), False, ('base', 'lid'))
        shot('lid_top_view.png', (cx, cy, cz + 400), (0, 1, 0), True, ('lid',))
        shot('base_top_view.png', (cx, cy, cz + 400), (0, 1, 0), True, ('base',))
        occ_base.isLightBulbOn = True; occ_lid.isLightBulbOn = True
        for o in pi: o.isLightBulbOn = True
        occ_plate.isLightBulbOn = True
    except:
        log('images failed: ' + traceback.format_exc())
    log('DONE')
    ui.messageBox('Готово. Лог: ' + os.path.join(OUT_DIR, 'script_log.txt'))
