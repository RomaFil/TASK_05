import sys, numpy as np, struct
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopoDS import TopoDS
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
r=STEPControl_Reader(); r.ReadFile(sys.argv[1]); r.TransferRoots(); s=r.OneShape()
sol=[]; ex=TopExp_Explorer(s,TopAbs_SOLID)
while ex.More():
    so=TopoDS.Solid(ex.Current()); b=Bnd_Box(); BRepBndLib.Add_s(so,b); lo=b.CornerMin(); hi=b.CornerMax()
    sol.append((so,tuple(round(v,2) for v in (lo.X(),lo.Y(),lo.Z(),hi.X(),hi.Y(),hi.Z())))); ex.Next()
base=[x for x in sol if x[1][2]<-26][0]; lid=[x for x in sol if x[1][5]>23.5][0]
def d(a,b):
    e=BRepExtrema_DistShapeShape(a,b); e.Perform(); return round(e.Value(),2)
names={0:'plate',5:'Pi board',6:'USB1',7:'USB2',8:'Eth'}
plate=sol[0]
print("lid-plate",d(lid[0],plate[0]))
for i in (5,6,7,8): print("base-",names[i],d(base[0],sol[i][0]))
# other Pi parts: min distance to base, list smallest few
ds=[]
for i,x in enumerate(sol):
    if i in (55,56): continue
    ds.append((d(base[0],x[0]),x[1]))
ds.sort(); print("base closest parts:",ds[:6])
dl=[]
for i,x in enumerate(sol):
    if i in (55,56) or x[1][2]<-1.7: continue
    dl.append((d(lid[0],x[0]),x[1]))
dl.sort(); print("lid closest parts (plate-side):",dl[:5])
print("plate J1/LED bodies:",[(x[1]) for x in sol[:5]])
def stl(fn):
    b=open(fn,'rb').read(); n=struct.unpack('<I',b[80:84])[0]
    a=np.frombuffer(b[84:],dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')]),count=n)
    v=a['v'].reshape(-1,3); return n,v.min(0).round(2),v.max(0).round(2)
for fn in ("Case_Base_print.stl","Case_Lid_print_flipped.stl"): print(fn,*stl((sys.argv[2] if len(sys.argv)>2 else "../output")+"/"+fn))
