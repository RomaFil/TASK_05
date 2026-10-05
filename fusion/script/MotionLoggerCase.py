# -*- coding: utf-8 -*-
# Корпус Motion Logger: Raspberry Pi 5 + материнська плата 85x56. Усі розміри в мм.
# Система координат P: лівий нижній кут плати = (0;0), Z=0 = верх плати (плата Z -1.62..0), Z вгору.
import adsk.core, adsk.fusion, traceback, math, os

# ---------------- ПАРАМЕТРИ ----------------
H = 20.0            # від верху плати Pi до низу плати Motion Logger = довжина стійок M2.5
                    # (2.57 пластик гребінки Pi + 8.5 гребінка-подовжувач + 8.5 гніздо плати = 19.57, стійка 20)
TUBE_OD = 8.4       # трубки-світловоди навколо світлодіодів
TUBE_BOT = 10.4     # низ трубки над платою (верх колби LED = 9.6)
CAV = 20.0          # внутрішня висота над платою (гребінка 8.5 + модуль 10 + запас 1.5)
W = 3.0             # стінки
FL = 3.0            # дно
LT = 4.0            # верх кришки
POST_H = 3.0        # стійка під Pi над дном
POST_D = 7.0        # діаметр стійок (можна розсверлити до ~5 мм)
HOLE_D = 2.7        # отвір під M2.5 (можна розсвердлити)
CB_D = 5.6          # заглиблення під головку гвинта
CB_DEP = 1.8
TONGUE = 1.2        # шип основи (замок)
SKIRT = 1.5         # внутрішня межа спідниці кришки від краю порожнини
STEP_Z = -2.0       # висота, з якої стінка основи звужується до шипа
GAP_LID = 0.2       # вертикальний зазор замка
PLATE_T = 1.62
CAVX0, CAVX1, CAVY0, CAVY1 = -1.0, 88.6, -2.2, 56.8
R_OUT = 3.0
try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
OUT_DIR = os.path.normpath(os.path.join(_HERE, "..", "output"))
IN_DIR = os.path.normpath(os.path.join(_HERE, "..", "inputs"))

HOLES = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]
LEDS = [(66.23, 11.0), (57.0, 11.0), (75.0, 11.5)]   # D1 червоний, D2 синій, D3 зелений
LED_WIN = 5.5
GPS = (21.9, 33.6, 38.5, 26.5)                       # центр x,y, розмір x,y (весь модуль +0.5)
SW = [dict(cx=77.5, cy=26.0, padx=75.5, pady=26.04),
      dict(cx=77.5, cy=44.58, padx=79.5, pady=44.54)]
POCKET = (8.5, 15.5)                                 # 8x15 з бібліотеки +0.5
POCKET_DEP = 2.0
SLOT = (4.0, 9.2)

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

    # ---------- імпорт плат ----------
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
    plate = imp('plate_clean.step', (-67.5, -47.5, 0))
    pi = imp('pi5_proxy.step', (0, 0, dz))
    for o in plate: o.component.name = 'Plate_Motion_Logger'
    for o in pi: o.component.name = 'Pi5_proxy'
    log('imported plate %d, pi %d' % (len(plate), len(pi)))

    # ---------- ОСНОВА ----------
    OX0, OX1, OY0, OY1 = CAVX0 - W, CAVX1 + W, CAVY0 - W, CAVY1 + W
    base = rrect(OX0, OY0, OX1, OY1, zfb, STEP_Z, R_OUT)
    uni(base, box(CAVX0 - TONGUE, CAVY0 - TONGUE, STEP_Z - 0.1, CAVX1 + TONGUE, CAVY1 + TONGUE, 0))
    dif(base, box(CAVX0, CAVY0, zft, CAVX1, CAVY1, 1))
    for (x, y) in HOLES:
        uni(base, cyl(x, y, zft - 0.1, pi_bot, POST_D))
    for (x, y) in HOLES:
        dif(base, cyl(x, y, zfb - 1, pi_bot + 0.1, HOLE_D))
        dif(base, cyl(x, y, zfb - 1, zfb + CB_DEP, CB_D))
    # вікна
    zt_usb = min(17.53 + dz + 0.8, -2.2)
    zb_eth = -0.66 + dz - 0.8
    zt_eth = 14.64 + dz + 0.8
    xr0, xr1 = CAVX1 - 0.5, OX1 + 1
    for (y0, y1, zb, zt) in ((2.28 - 0.5, 18.22 + 0.5, zb_eth, zt_eth),
                             (21.75 - 0.5, 36.25 + 0.5, zb_eth, zt_usb),
                             (39.75 - 0.5, 54.25 + 0.5, zb_eth, zt_usb)):
        dif(base, box(xr0, y0, zb, xr1, y1, zt))
    zb_b, zt_b = 0.24 + dz - 2.0, 4.68 + dz + 2.0
    for (x0, x1) in ((6.73 - 2.0, 15.67 + 2.0), (22.2 - 2.0, 29.4 + 2.0), (35.6 - 2.0, 42.8 + 2.0)):
        dif(base, box(x0, OY0 - 1, zb_b, x1, CAVY0 + 0.5, zt_b))
    dif(base, box(OX0 - 1, 21.0, zft, CAVX0 + 0.5, 35.0, pi_bot + 1.0))   # microSD
    # вентиляція під процесором
    for k in range(-2, 3):
        dif(base, box(33.15 + 3.6 * k - 1.2, 22.75 - 9, zfb - 1, 33.15 + 3.6 * k + 1.2, 22.75 + 9, zft + 0.1))
    occ_base = newcomp('Case_Base')
    addbody(occ_base, base, 'Base')

    # ---------- КРИШКА ----------
    lid = rrect(OX0, OY0, OX1, OY1, zlb, zlt, R_OUT)
    dif(lid, box(CAVX0 - SKIRT, CAVY0 - SKIRT, zlb - 1, CAVX1 + SKIRT, CAVY1 + SKIRT, 0))
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
    for s in SW:
        dif(lid, box(s['cx'] - POCKET[0] / 2, s['cy'] - POCKET[1] / 2, zlt - POCKET_DEP, s['cx'] + POCKET[0] / 2, s['cy'] + POCKET[1] / 2, zlt + 1))
        dif(lid, box(s['padx'] - SLOT[0] / 2, s['pady'] - SLOT[1] / 2, CAV - 1, s['padx'] + SLOT[0] / 2, s['pady'] + SLOT[1] / 2, zlt + 1))
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
