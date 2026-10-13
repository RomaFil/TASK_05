{ Motion Logger: silk arcs inside components thinner than 0.15 mm -> 0.15 mm }
Procedure FixArcWidth;
Var
   Board    : IPCB_Board;
   CompIter : IPCB_BoardIterator;
   Comp     : IPCB_Component;
   GIter    : IPCB_GroupIterator;
   Prim     : IPCB_Arc;
   Cnt      : Integer;
   Seen     : Integer;
Begin
   Board := PCBServer.GetCurrentPCBBoard;
   If Board = Nil Then
   Begin
      ShowMessage('No PCB document is active');
      Exit;
   End;
   Cnt := 0;
   Seen := 0;
   PCBServer.PreProcess;
   CompIter := Board.BoardIterator_Create;
   CompIter.AddFilter_ObjectSet(MkSet(eComponentObject));
   CompIter.AddFilter_LayerSet(AllLayers);
   CompIter.AddFilter_Method(eProcessAll);
   Comp := CompIter.FirstPCBObject;
   While Comp <> Nil Do
   Begin
      GIter := Comp.GroupIterator_Create;
      GIter.AddFilter_ObjectSet(MkSet(eArcObject));
      Prim := GIter.FirstPCBObject;
      While Prim <> Nil Do
      Begin
         If (Prim.Layer = eTopOverlay) Or (Prim.Layer = eBottomOverlay) Then
         Begin
            Inc(Seen);
            If Prim.LineWidth < MilsToCoord(5.9) Then
            Begin
               Prim.BeginModify;
               Prim.LineWidth := MilsToCoord(5.9055);
               Prim.EndModify;
               Inc(Cnt);
            End;
         End;
         Prim := GIter.NextPCBObject;
      End;
      Comp.GroupIterator_Destroy(GIter);
      Comp := CompIter.NextPCBObject;
   End;
   Board.BoardIterator_Destroy(CompIter);
   PCBServer.PostProcess;
   Board.ViewManager_FullUpdate;
   ShowMessage('Silk arcs seen: ' + IntToStr(Seen) + ', widened to 0.15 mm: ' + IntToStr(Cnt));
End;
