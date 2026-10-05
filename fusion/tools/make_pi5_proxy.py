from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound
from OCP.gp import gp_Pnt, gp_Ax2, gp_Dir
comp=TopoDS_Compound(); B=BRep_Builder(); B.MakeCompound(comp)
def box(x0,y0,z0,x1,y1,z1): return BRepPrimAPI_MakeBox(gp_Pnt(x0,y0,z0),gp_Pnt(x1,y1,z1)).Shape()
board=box(0,0,0.03,85,56,1.31)
for (x,y) in ((3.5,3.5),(61.5,3.5),(3.5,52.5),(61.5,52.5)):
    cyl=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x,y,-1),gp_Dir(0,0,1)),1.35,4).Shape()
    board=BRepAlgoAPI_Cut(board,cyl).Shape()
B.Add(comp,board)
parts=[(70.46,21.75,-0.17,88.0,36.25,17.53),(70.33,39.75,-0.17,87.78,54.25,17.36),(66.45,2.28,-0.66,88.05,18.22,14.64),
(6.73,-1.2,0.34,15.67,6.12,4.6),(22.2,-1.63,0.24,29.4,6.87,4.68),(35.6,-1.63,0.24,42.8,6.87,4.68),
(2.25,22.11,-1.42,13.65,34.06,0.0),(7.1,49.96,1.34,57.9,55.04,3.88),(24.66,14.26,2.3,41.64,31.24,3.71)]
for p in parts: B.Add(comp,box(*p))
for k in range(20):
    for y in (51.23,53.77):
        x=8.37+2.54*k; B.Add(comp,box(x-0.32,y-0.32,-0.56,x+0.32,y+0.32,9.88))
w=STEPControl_Writer(); w.Transfer(comp,STEPControl_AsIs); w.Write("../inputs/pi5_proxy.step")
