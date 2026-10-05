import sys
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.TopoDS import TopoDS
r=STEPControl_Reader(); r.ReadFile(sys.argv[1]); r.TransferRoots(); s=r.OneShape()
sol=[]
ex=TopExp_Explorer(s,TopAbs_SOLID)
while ex.More():
    so=TopoDS.Solid(ex.Current()); b=Bnd_Box(); BRepBndLib.Add_s(so,b); lo=b.CornerMin(); hi=b.CornerMax()
    p=GProp_GProps(); BRepGProp.VolumeProperties_s(so,p)
    sol.append((so,[round(v,2) for v in (lo.X(),lo.Y(),lo.Z(),hi.X(),hi.Y(),hi.Z())],p.Mass())); ex.Next()
print(len(sol))
big=[(i,x[1],round(x[2])) for i,x in enumerate(sol) if x[2]>3000 or x[1][5]-x[1][2]>40]
for b in big: print(b)
import pickle
def vol(sh):
    p=GProp_GProps(); BRepGProp.VolumeProperties_s(sh,p); return p.Mass()
base=[x for x in sol if x[1][2]<-26 and x[1][5]<1][0]
lids=[x for x in sol if x[1][5]>23 and x[1][2]<0 and x[1][2]>-3]
print("base",base[1],"lids",[l[1] for l in lids])
lid=lids[0]
others=[x for x in sol if x not in [base]+lids]
print("interference (volume mm3):")
for name,A in (("base",base),("lid",lid)):
    tot=0; hits=[]
    for o in others:
        c=BRepAlgoAPI_Common(A[0],o[0]); v=vol(c.Shape()) if c.IsDone() else -1
        if v>0.01: hits.append((o[1],round(v,2)))
    print(name,"hits:",hits)
print("base vs lid:",round(vol(BRepAlgoAPI_Common(base[0],lid[0]).Shape()),3))
