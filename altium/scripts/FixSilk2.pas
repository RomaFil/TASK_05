{ Motion Logger: silk tracks inside components thinner than 0.15 mm -> 0.15 mm }
Procedure FixSilkWidth2;
Var
   Board    : IPCB_Board;
   CompIter : IPCB_BoardIterator;
   Comp     : IPCB_Component;
   GIter    : IPCB_GroupIterator;
   Prim     : IPCB_Primitive;
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
      GIter.AddFilter_ObjectSet(MkSet(eTrackObject));
      Prim := GIter.FirstPCBObject;
      While Prim <> Nil Do
      Begin
         If (Prim.Layer = eTopOverlay) Or (Prim.Layer = eBottomOverlay) Then
         Begin
            Inc(Seen);
            If Prim.Width < MilsToCoord(5.9) Then
            Begin
               Prim.BeginModify;
               Prim.Width := MilsToCoord(5.9055);
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
   ShowMessage('Silk tracks seen: ' + IntToStr(Seen) + ', widened to 0.15 mm: ' + IntToStr(Cnt));
End;
