# -*- coding: utf-8 -*-
# Корпус Motion Logger (версія 3, 13.10.2026): Pi 5 + плата 85 x 60,77 (виступає ліворуч на ~20 мм), товста кришка з нішами під кнопки (без рамок),
# вікна портів з 45-градусним дахом (друк без мостів), світловоди товщі, отвори під гвинти ⌀2,9.
# Усі розміри в мм. Система координат P: лівий нижній кут Pi 5 = (0;0), Z=0 = верх плати Motion Logger, Z вгору.
# Зв'язок з Altium (пін 1 J1 = початок): P = Altium + (8.37; 51.23).
import adsk.core, adsk.fusion, traceback, math, os

# ---------------- ПАРАМЕТРИ ----------------
H = 11.0            # від верху плати Pi до низу плати Motion Logger = довжина стійок M2.5 (як у HAT)
                    # (2.57 пластик гребінки Pi + 8.5 гніздо J1 на платі = 11.07, стійка 11)
TUBE_OD = 8.0       # трубки-світловоди навколо світлодіодів
TUBE_BOT = 10.4     # низ трубки над платою (верх колби LED = 9.6)
CAV = 20.0          # внутрішня висота над платою (гребінка 8.5 + модуль 10 + запас 1.5)
W = 3.0             # стінки
FL = 3.0            # дно
LT = 7.5            # верх кришки (ніша кнопки 5,5 + дно 2,0)
POST_H = 3.0        # стійка під Pi над дном
POST_D = 7.0        # діаметр стійок (можна розсверлити до ~5 мм)
HOLE_D = 2.9        # отвір під M2.5 (при друку звужується на ~0,2)
CB_D = 5.6          # заглиблення під головку гвинта
CB_DEP = 1.8
TONGUE = 1.2        # шип основи (замок)
SKIRT = 1.5         # внутрішня межа спідниці кришки від краю порожнини
STEP_Z = 11.0       # висота, з якої стінка основи звужується до шипа (даху вікон USB до +9,3)
TONGUE_H = 2.0      # висота шипа
GAP_LID = 0.2       # вертикальний зазор замка
PLATE_T = 1.5
PX0, PX1, PY0, PY1 = -19.80, 65.20, -0.77, 60.00      # габарит плати (R2)
CAVX0, CAVX1, CAVY0, CAVY1 = -20.8, 88.6, -2.2, 60.8
R_OUT = 3.0
try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
OUT_DIR = os.path.normpath(os.path.join(_HERE, "..", "output"))
IN_DIR = os.path.normpath(os.path.join(_HERE, "..", "inputs"))

HOLES = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]
LEDS = [(49.01, 19.48), (49.01, 11.86), (49.01, 4.24)]   # D1 червоний, D2 синій, D3 зелений (колонка, крок 7,62)
LED_WIN = 5.5
GPS = (0.81, 35.43, 38.5, 26.5)                      # центр x,y, розмір x,y (весь модуль +0.5)
PLATE_HOLES = [(3.5, 3.5, 2.7), (61.5, 3.5, 2.7), (3.5, 52.5, 2.7), (61.5, 52.5, 2.7),
               (-14.49, 45.03, 3.2), (-14.49, 25.83, 3.2), (16.71, 45.03, 3.2), (16.71, 25.83, 3.2)]
BTN = [(-10.5, 9.0), (19.0, 9.0)]                   # SW1, SW2: рамки на кришці над падами (пади SW1 (-11.9;6.8), SW2 (13.5;6.8))
POCKET = (15.5, 19.5)                                # реальний модуль HW-483 (KY-004) 15 x 19 мм (виміряв Роман 12.10) +0.5 зазор
POCKET_DEP = 5.5                                     # глибина ніші в товстій кришці (модуль ~6,6 мм => виступ ~1 мм)
SLOT = (12.0, 4.5)                                   # щілина під дроти: ширина по x, глибина від нижнього краю ніші
SUPPORTS = [(-17.0, 6.0), (-17.0, 54.0)]             # опори під виступ плати зліва
SUP_D = 6.0
SD_WIN = (-6.0, 20.5, 13.0, 35.5)                    # вікно в дні під microSD (знизу плати Pi)

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

def build(app, ui):
    app.preferences.generalPreferences.defaultModelingOrientation = adsk.core.DefaultModelingOrientations.ZUpModelingOrientation
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.DirectDesignType
    root = design.rootComponent
    log('units=' + design.unitsManager.defaultLengthUnits)
    bm = adsk.fusion.TemporaryBRepManager.get()

    def P(x, y, z): return adsk.core.Point3D.create(x * MM, y * MM, z * MM)
    def V(x, y, z): return adsk.core.Vector3D.create(x, y, z)
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
        """45-градусний дах над вікном: призма-ромб вздовж осі, зрізана на плоскій частині ROOF_FLAT."""
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

    # ---------- Z-рівні ----------
    zpt = -PLATE_T - H            # верх плати Pi
    dz = zpt - 1.31               # зсув STEP Pi по Z
    pi_bot = 0.03 + dz
    zft = pi_bot - POST_H         # верх дна
    zfb = zft - FL                # низ дна
    log('H=%s zpt=%.2f dz=%.2f pi_bot=%.2f floor top=%.2f bottom=%.2f' % (H, zpt, dz, pi_bot, zft, zfb))
    zlt = CAV + LT                # верх кришки
    zlb = STEP_Z + GAP_LID        # низ спідниці кришки (зазор над сходинкою основи)

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
    pi = imp('pi5_proxy.step', (0, 0, dz))
    for o in pi: o.component.name = 'Pi5_proxy'
    plate_b = rrect(PX0, PY0, PX1, PY1, -PLATE_T, 0, 2.0)
    for (x, y, d) in PLATE_HOLES:
        dif(plate_b, cyl(x, y, -PLATE_T - 1, 1, d))
    occ_plate = newcomp('Plate_Motion_Logger')
    addbody(occ_plate, plate_b, 'Plate')
    log('imported pi %d' % len(pi))

    # ---------- ОСНОВА ----------
    OX0, OX1, OY0, OY1 = CAVX0 - W, CAVX1 + W, CAVY0 - W, CAVY1 + W
    ztong = STEP_Z + TONGUE_H
    base = rrect(OX0, OY0, OX1, OY1, zfb, STEP_Z, R_OUT)
    uni(base, box(CAVX0 - TONGUE, CAVY0 - TONGUE, STEP_Z - 0.1, CAVX1 + TONGUE, CAVY1 + TONGUE, ztong))
    dif(base, box(CAVX0, CAVY0, zft, CAVX1, CAVY1, ztong + 1))
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
    # вентиляція під процесором
    for k in range(-2, 3):
        dif(base, box(33.15 + 3.6 * k - 1.2, 22.75 - 9, zfb - 1, 33.15 + 3.6 * k + 1.2, 22.75 + 9, zft + 0.1))
    occ_base = newcomp('Case_Base')
    addbody(occ_base, base, 'Base')

    # ---------- КРИШКА ----------
    lid = rrect(OX0, OY0, OX1, OY1, zlb, zlt, R_OUT)
    dif(lid, box(CAVX0 - SKIRT, CAVY0 - SKIRT, zlb - 1, CAVX1 + SKIRT, CAVY1 + SKIRT, ztong))
    dif(lid, box(CAVX0, CAVY0, -0.5, CAVX1, CAVY1, CAV))
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
        dif(lid, box(bx - SLOT[0] / 2, by - POCKET[1] / 2, CAV - 1, bx + SLOT[0] / 2, by - POCKET[1] / 2 + SLOT[1], zlt + 1))   # щілина під дроти біля нижнього краю ніші (де піни модуля)
    occ_lid = newcomp('Case_Lid')
    addbody(occ_lid, lid, 'Lid')

    # ---------- кришка догори дном для друку ----------
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

    # ---------- перевірка перетинів ----------
    try:
        ents = adsk.core.ObjectCollection.create()
        for occ in root.allOccurrences:
            if occ.name.startswith('Case_Lid_for_print'):
                continue
            for bd in occ.bRepBodies:
                ents.add(bd)
        res = design.analyzeInterference(design.createInterferenceInput(ents))
        log('interferences: %d' % res.count)
        for r in res:
            n1 = r.entityOne.parentComponent.name
            n2 = r.entityTwo.parentComponent.name
            if n1 == n2:
                continue
            log('  %s <-> %s vol=%.4f cm3' % (n1, n2, r.interferenceBody.volume))
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
    for bd, fn in ((occ_base.component.bRepBodies.item(0), 'Case_Base_print.stl'),
                   (occ_pr.component.bRepBodies.item(0), 'Case_Lid_print_flipped.stl')):
        try:
            o = em.createSTLExportOptions(bd, os.path.join(OUT_DIR, fn))
            o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
            o.sendToPrintUtility = False
            em.execute(o)
            log(fn + ' ok')
        except:
            log('stl failed ' + fn + ': ' + traceback.format_exc())
    log('DONE')
    ui.messageBox('Готово. Лог: ' + os.path.join(OUT_DIR, 'script_log.txt'))
