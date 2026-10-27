# -*- coding: utf-8 -*-
# Корпус Motion Logger v4 (27.10.2026): v3 + заокруглені ребра, соти для вентиляції, вигравіюваний напис.
# Усі розміри в мм. Система координат P: лівий нижній кут Pi 5 = (0;0), Z=0 = верх плати Motion Logger, Z вгору.
# Зв'язок з Altium (пін 1 J1 = початок): P = Altium + (8.37; 51.23).
# Друк без підтримок: край біля столу має фаску-закруглення не гостріше 45 градусів, вікна портів з дахом 45 градусів,
# соти плоским верхом (міст 4 мм), напис і соти на кришці вертикальні (кришка друкується догори дном).
import adsk.core, adsk.fusion, traceback, math, os

# ---------------- ПАРАМЕТРИ ----------------
H = 11.0
TUBE_OD = 8.0
TUBE_BOT = 10.4
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
SLOT = (12.0, 4.5)
SUPPORTS = [(-17.0, 6.0), (-17.0, 54.0)]
SUP_D = 6.0
SD_WIN = (-6.0, 20.5, 13.0, 35.5)

# соти: a = радіус описаного кола шестикутника (сторона), T = товщина перемичок
HEX_A_WALL, HEX_A_LID, HEX_T = 4.0, 3.5, 1.6
# напис: (текст, центр x, центр y, макс. ширина, макс. висота), глибина різьби
TEXTS = [('AJAX', 55.5, 40.0, 52.0, 11.0, 18), ('MOTION LOGGER', 55.5, 29.0, 58.0, 5.5, 4)]   # + міжлітерний інтервал
TEXT_DEP = 0.7

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

def make_text_solids(app, bm, txt, cx, cy, tw, th, zc, dep, spacing):
    """Текст через ескіз у допоміжному документі; повертає тимчасові тіла (товщина 2*dep), центр (cx;cy), середина по z = zc."""
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    try:
        des = adsk.fusion.Design.cast(app.activeProduct)
        rt = des.rootComponent
        h = th
        bodies = []
        for it in range(4):
            sk = rt.sketches.add(rt.xYConstructionPlane)
            ti = sk.sketchTexts.createInput2(txt, h * MM)
            ti.setAsMultiLine(adsk.core.Point3D.create(-30, -3, 0), adsk.core.Point3D.create(30, 3, 0),
                              adsk.core.HorizontalAlignments.CenterHorizontalAlignment,
                              adsk.core.VerticalAlignments.MiddleVerticalAlignment, spacing)
            try:
                ti.fontName = 'Arial'
                ti.textStyle = adsk.fusion.TextStyles.TextStyleBold
            except:
                log('font style failed: ' + traceback.format_exc())
            stx = sk.sketchTexts.add(ti)
            log('text %r it=%d h=%.2f' % (txt, it, h))
            ext = rt.features.extrudeFeatures
            # текст не дає профілів у sketch.profiles, видавлюємо SketchText напряму (контр-форми A, O, R враховуються самі)
            ei = ext.createInput(stx, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            ei.setDistanceExtent(False, adsk.core.ValueInput.createByReal(2 * dep * MM))
            ef = ext.add(ei)
            bodies = [ef.bodies.item(i) for i in range(ef.bodies.count)]
            mn = [1e9, 1e9, 1e9]; mx = [-1e9, -1e9, -1e9]
            for b in bodies:
                bb = b.boundingBox
                for i, (lo, hi) in enumerate(((bb.minPoint.x, bb.maxPoint.x), (bb.minPoint.y, bb.maxPoint.y), (bb.minPoint.z, bb.maxPoint.z))):
                    mn[i] = min(mn[i], lo); mx[i] = max(mx[i], hi)
            wmm, hmm = (mx[0] - mn[0]) / MM, (mx[1] - mn[1]) / MM
            s = min(tw / wmm, th / hmm)
            log('text %r size %.1f x %.1f mm, scale %.3f' % (txt, wmm, hmm, s))
            if abs(s - 1) < 0.03:
                break
            ef.deleteMe(); sk.deleteMe()
            h *= s
        keep = bodies
        log('text %r bodies=%d' % (txt, len(bodies)))
        mn = [1e9, 1e9]; mx = [-1e9, -1e9]
        for b in keep:
            bb = b.boundingBox
            mn[0] = min(mn[0], bb.minPoint.x); mn[1] = min(mn[1], bb.minPoint.y)
            mx[0] = max(mx[0], bb.maxPoint.x); mx[1] = max(mx[1], bb.maxPoint.y)
        m = adsk.core.Matrix3D.create()
        m.translation = V(cx * MM - (mn[0] + mx[0]) / 2, cy * MM - (mn[1] + mx[1]) / 2, zc * MM - dep * MM)
        out = []
        for b in keep:
            cp = bm.copy(b)
            bm.transform(cp, m)
            out.append(cp)
        return out
    finally:
        doc.close(False)

def build(app, ui):
    bm = adsk.fusion.TemporaryBRepManager.get()
    zpt = -PLATE_T - H
    zlt = CAV + LT

    # ---------- напис: готуємо до створення основного документа ----------
    text_bodies = []
    for (txt, cx, cy, tw, th, sp) in TEXTS:
        try:
            text_bodies += make_text_solids(app, bm, txt, cx, cy, tw, th, zlt, TEXT_DEP, sp)
        except:
            log('TEXT FAILED %r: %s' % (txt, traceback.format_exc()))
    log('text bodies total: %d' % len(text_bodies))

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
    def roof(axis, a0, a1, b0, b1, zt):
        w = b1 - b0
        sd = w / math.sqrt(2)
        if axis == 'x':
            c = P((a0 + a1) / 2, (b0 + b1) / 2, zt)
            d = bm.createBox(adsk.core.OrientedBoundingBox3D.create(c, V(1, 0, 0), V(0, SQ, SQ), (a1 - a0) * MM, sd * MM, sd * MM))
            dif(d, box(a0 - 1, b0 - 1, zt + (w - ROOF_FLAT) / 2, a1 + 1, b1 + 1, zt + w))
        else:
            c = P((b0 + b1) / 2, (a0 + a1) / 2, zt)
            d = bm.createBox(adsk.core.OrientedBoundingBox3D.create(c, V(0, 1, 0), V(SQ, 0, SQ), (a1 - a0) * MM, sd * MM, sd * MM))
            dif(d, box(b0 - 1, a0 - 1, zt + (w - ROOF_FLAT) / 2, b1 + 1, a1 + 1, zt + w))
        return d
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
    base = soft_blank(OX0, OY0, OX1, OY1, zfb, STEP_Z, R_OUT, 'bottom')
    uni(base, rrect(CAVX0 - TONGUE, CAVY0 - TONGUE, CAVX1 + TONGUE, CAVY1 + TONGUE, STEP_Z - 0.1, ztong, R_OUT - (W - TONGUE)))
    dif(base, rrect(CAVX0, CAVY0, CAVX1, CAVY1, zft, ztong + 1, R_OUT - W))
    for (x, y) in SUPPORTS:
        uni(base, cyl(x, y, zft - 0.1, -PLATE_T - 0.3, SUP_D))
    for (x, y) in HOLES:
        uni(base, cyl(x, y, zft - 0.1, pi_bot, POST_D))
    for (x, y) in HOLES:
        dif(base, cyl(x, y, zfb - 1, pi_bot + 0.1, HOLE_D))
        dif(base, cyl(x, y, zfb - 1, zfb + CB_DEP, CB_D))
    # вікна
    zt_usb = 17.53 + dz + 0.8
    zb_eth = -0.66 + dz - 0.8
    zt_eth = 14.64 + dz + 0.8
    xr0, xr1 = CAVX1 - 0.5, OX1 + 1
    for (y0, y1, zb, zt) in ((2.28 - 0.5, 18.22 + 0.5, zb_eth, zt_eth),
                             (21.75 - 0.5, 36.25 + 0.5, zb_eth, zt_usb),
                             (39.75 - 0.5, 54.25 + 0.5, zb_eth, zt_usb)):
        wnd = box(xr0, y0, zb, xr1, y1, zt)
        uni(wnd, roof('x', xr0, xr1, y0, y1, zt))
        dif(base, wnd)
    zb_b, zt_b = 0.24 + dz - 2.0, 4.68 + dz + 2.0
    for (x0, x1) in ((6.73 - 2.0, 15.67 + 2.0), (22.2 - 2.0, 29.4 + 2.0), (35.6 - 2.0, 42.8 + 2.0)):
        wnd = box(x0, OY0 - 1, zb_b, x1, CAVY0 + 0.5, zt_b)
        if x1 - x0 > 10:
            uni(wnd, roof('y', OY0 - 1, CAVY0 + 0.5, x0, x1, zt_b))
        dif(base, wnd)
    dif(base, box(SD_WIN[0], SD_WIN[1], zfb - 1, SD_WIN[2], SD_WIN[3], zft + 0.1))   # microSD знизу
    for k in range(-2, 3):                                                          # вентиляція під процесором
        dif(base, box(33.15 + 3.6 * k - 1.2, 22.75 - 9, zfb - 1, 33.15 + 3.6 * k + 1.2, 22.75 + 9, zft + 0.1))
    # соти на задній (+y) і лівій (-x) стінках основи
    zlo, zhi = zft + 1.5, 9.5
    n_hex = 0
    ya, yb = CAVY1 - 0.3, OY1 + 1
    for (u, v) in hex_grid(-15.0, 82.0, zlo, zhi, HEX_A_WALL, HEX_T):
        dif(base, hexcut(u, (ya + yb) / 2, v, (1, 0, 0), (0, 0, 1), HEX_A_WALL, yb - ya)); n_hex += 1
    xa, xb = OX0 - 1, CAVX0 + 0.3
    for (u, v) in hex_grid(OY0 + R_OUT + 3.0, OY1 - R_OUT - 3.0, zlo, zhi, HEX_A_WALL, HEX_T):
        dif(base, hexcut((xa + xb) / 2, u, v, (0, 1, 0), (0, 0, 1), HEX_A_WALL, xb - xa)); n_hex += 1
    log('wall hexes: %d' % n_hex)
    occ_base = newcomp('Case_Base')
    bd_base = addbody(occ_base, base, 'Base')

    # ---------- КРИШКА ----------
    lid = soft_blank(OX0, OY0, OX1, OY1, zlb, zlt, R_OUT, 'top')
    dif(lid, rrect(CAVX0 - SKIRT, CAVY0 - SKIRT, CAVX1 + SKIRT, CAVY1 + SKIRT, zlb - 1, ztong, R_OUT - (W - SKIRT)))
    dif(lid, rrect(CAVX0, CAVY0, CAVX1, CAVY1, -0.5, CAV, R_OUT - W))
    for (x, y) in HOLES:
        uni(lid, cyl(x, y, 0, CAV + 0.5, POST_D))
    for (x, y) in HOLES:
        dif(lid, cyl(x, y, -1, zlt + 1, HOLE_D))
        dif(lid, cyl(x, y, zlt - CB_DEP, zlt + 1, CB_D))
    for (x, y) in LEDS:
        uni(lid, cyl(x, y, TUBE_BOT, CAV + 0.5, TUBE_OD))
    for (x, y) in LEDS:
        dif(lid, cyl(x, y, TUBE_BOT - 1, zlt + 1, LED_WIN))
    gx, gy, gw, gh = GPS
    dif(lid, box(gx - gw / 2, gy - gh / 2, CAV - 1, gx + gw / 2, gy + gh / 2, zlt + 1))
    for (bx, by) in BTN:
        dif(lid, box(bx - POCKET[0] / 2, by - POCKET[1] / 2, zlt - POCKET_DEP, bx + POCKET[0] / 2, by + POCKET[1] / 2, zlt + 1))
        dif(lid, box(bx - SLOT[0] / 2, by - POCKET[1] / 2, CAV - 1, bx + SLOT[0] / 2, by - POCKET[1] / 2 + SLOT[1], zlt + 1))
    # соти на верху кришки (над правою частиною Pi): вихід гарячого повітря
    n_lid = 0
    for (u, v) in hex_grid(66.8, 87.6, -1.0, 24.0, HEX_A_LID, HEX_T):
        dif(lid, hexcut(u, v, (CAV - 0.5 + zlt + 1) / 2, (1, 0, 0), (0, 1, 0), HEX_A_LID, zlt + 1 - (CAV - 0.5))); n_lid += 1
    log('lid hexes: %d' % n_lid)
    # напис (вигравіюваний)
    for tb in text_bodies:
        dif(lid, bm.copy(tb))
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
