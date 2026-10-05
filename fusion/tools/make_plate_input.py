# Робить fusion/inputs/plate_clean.step зі STEP плати з Altium:
# лишає плату (тіло 0), гніздо J1 (10) і три колби світлодіодів (11, 16, 21);
# виводи резисторів і світлодіодів (до 27 мм униз) і самі резистори відкидаються.
# Запуск: python make_plate_input.py ../../altium/Fab/Motion_Logger_board.step ../inputs/plate_clean.step
import sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound

KEEP = (0, 10, 11, 16, 21)   # індекси тіл у порядку обходу STEP

r = STEPControl_Reader(); r.ReadFile(sys.argv[1]); r.TransferRoots()
comp = TopoDS_Compound(); b = BRep_Builder(); b.MakeCompound(comp)
ex = TopExp_Explorer(r.OneShape(), TopAbs_SOLID); i = 0
while ex.More():
    if i in KEEP:
        b.Add(comp, ex.Current())
    ex.Next(); i += 1
w = STEPControl_Writer(); w.Transfer(comp, STEPControl_AsIs); w.Write(sys.argv[2])
print("тіл у файлі:", len(KEEP), "з", i)
