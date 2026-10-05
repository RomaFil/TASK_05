import sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID, TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
r=STEPControl_Reader(); r.ReadFile(sys.argv[1]); r.TransferRoots(); s=r.OneShape()
sol=[]; ex=TopExp_Explorer(s,TopAbs_SOLID)
while ex.More():
    so=TopoDS.Solid(ex.Current()); b=Bnd_Box(); BRepBndLib.Add_s(so,b); lo=b.CornerMin(); hi=b.CornerMax()
    sol.append((so,(lo.X(),lo.Y(),lo.Z(),hi.X(),hi.Y(),hi.Z()))); ex.Next()
def cat(bx):
    if bx[2]<-27: return 'base'
    if bx[5]>23.5: return 'lid'
    if bx[5]<=0.01 and bx[2]>=-1.7 and bx[3]-bx[0]>80: return 'plate'
    return 'other'
col={'base':'#c0392b','lid':'#2980b9','plate':'#27ae60','other':'#7f8c8d'}
def section(axis,val,fn,title):
    fig,ax=plt.subplots(figsize=(13,7))
    if axis=='y': pln=gp_Pln(gp_Pnt(0,val,0),gp_Dir(0,1,0))
    else: pln=gp_Pln(gp_Pnt(val,0,0),gp_Dir(1,0,0))
    for so,bx in sol:
        if axis=='y' and not (bx[1]-0.01<=val<=bx[4]+0.01): continue
        if axis=='x' and not (bx[0]-0.01<=val<=bx[3]+0.01): continue
        sec=BRepAlgoAPI_Section(so,pln); sec.Build()
        e=TopExp_Explorer(sec.Shape(),TopAbs_EDGE)
        while e.More():
            c=BRepAdaptor_Curve(TopoDS.Edge(e.Current()))
            d=GCPnts_QuasiUniformDeflection(c,0.05)
            if d.IsDone():
                pts=np.array([[d.Value(i).X(),d.Value(i).Y(),d.Value(i).Z()] for i in range(1,d.NbPoints()+1)])
                h=pts[:,0] if axis=='y' else pts[:,1]
                ax.plot(h,pts[:,2],color=col[cat(bx)],lw=1.2)
            e.Next()
    ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_title(title); ax.set_xlabel('x (mm)' if axis=='y' else 'y (mm)'); ax.set_ylabel('z (mm), 0 = верх плати')
    fig.savefig(fn,dpi=110,bbox_inches='tight')
section('y',11.0,'sec_y11.png','Переріз y=11 (LED, Ethernet): червоний — основа, синій — кришка, зелений — плата')
section('x',77.5,'sec_x775.png','Переріз x=77.5 (кнопки, USB): червоний — основа, синій — кришка, зелений — плата')
