import wx
from wx.lib.floatcanvas import NavCanvas, FloatCanvas
# import wx.svg
from .comparison_dialog_ui import ComparisonOptionsDialog
from .pcb_components import PcbBoard, get_offset, IU_PER_MM
from .selection_dialog_events import ComponentSelectionDialog
from .comp_analysis_events import CompAnalysisDialog

# TODO Maybe call layout locally instead of self.layout everywhere

ALIGN_METHOD_CHOICES = ["None", "Edge", "Component"]
ALIGN_CORNER_CHOICES = ["Top Left", "Top Right", "Bottom Right", "Bottom Left"]

ERASE_NAME = "Stuff to be Erased"
WRITE_NAME = "Stuff to be Written"

class BoardComparisonWindow(ComparisonOptionsDialog):

    def __init__(self):
        super(BoardComparisonWindow, self).__init__(None)

        self.old_board_path = None
        self.old_board = None
        self.new_board = None
        self.erase_paths = None
        self.write_paths = None
        self.align_method = "None"
        self.comparison_method = "component"
        self.export_data = []
        self.log_sizer = None

        self.DialogInit()

    def DialogInit(self):
        op_sizer = self.PanelOperations.GetSizer()
        self.board_vis = BoardVisPanel( self.PanelOperations, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        op_sizer.Add(self.board_vis, 2, wx.EXPAND | wx.ALL, 5)

        align_sizer = wx.BoxSizer(wx.VERTICAL)
        self.rbAlignMethod = wx.RadioBox(self.PanelAlignBoards, wx.ID_ANY,  \
                                         "Align Method", choices=ALIGN_METHOD_CHOICES, style=wx.RA_SPECIFY_ROWS)
        align_sizer.Add(self.rbAlignMethod)

        self.choiceOldAlign = wx.Choice(self.PanelAlignBoards)
        self.choiceNewAlign = wx.Choice(self.PanelAlignBoards)
        choice_sizer = wx.BoxSizer(wx.VERTICAL)
        choice_sizer.Add(self.choiceOldAlign)
        choice_sizer.Add(self.choiceNewAlign)
        align_sizer.Add(choice_sizer)

        self.choiceAlignCorner = wx.Choice(self.PanelAlignBoards, choices=ALIGN_CORNER_CHOICES)
        self.choiceAlignCorner.SetSelection(0)
        align_sizer.Add(self.choiceAlignCorner)

        self.buttonAlignBoards = wx.Button(self.PanelAlignBoards, label="Align")
        self.buttonAlignBoards.Bind(wx.EVT_BUTTON, lambda event: self.UpdateBoardAlignment())
        align_sizer.Add(self.buttonAlignBoards, flag=wx.ALIGN_RIGHT)

        self.PanelAlignBoards.SetSizer(align_sizer)

        self.choiceNewAlign.Hide()
        self.choiceOldAlign.Hide()
        self.choiceAlignCorner.Hide()

        self.rbAlignMethod.Bind(wx.EVT_RADIOBOX, self.AlignMethodChanged)

        self.UseCurrentBoard(None)
        self.Layout()

        if not self.log_sizer:
            self.log_sizer = wx.BoxSizer(wx.VERTICAL)
            self.PanelLog.SetSizer(self.log_sizer)
            # self.AddToLog("Dialog init!")
        pass

    def OnClose(self, event):
        self.DestroyChildren()
        self.Destroy()
    
    def AddToLog(self, log_text):
        # new_label = wx.StaticText(self.PanelLog, label=f"{self.log_sizer.GetItemCount() + 1}- {log_text}")
        new_label = wx.StaticText(self.PanelLog, label=log_text)
        self.log_sizer.Add(new_label)
        
        
        self.Layout()
        self.PanelLog.ScrollPages(1)

    def OpenFileDialog(self):
        ofd = wx.FileDialog(parent=None, message="Select Board File", \
                            wildcard = "KiCad PCB files (*.kicad_pcb)|*.kicad_pcb", style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if ofd.ShowModal() == wx.ID_CANCEL:
            return None
        
        pathname = ofd.GetPath()

        ofd.Destroy()

        return pathname

    # Find some way to combine these two functions
    def UploadOldFile(self, event):
        self.old_board_path = self.OpenFileDialog()

        if self.old_board_path:            
            self.old_board = PcbBoard(path=self.old_board_path)

            self.LabelOldFilePath.SetLabelText(self.old_board_path)
            # self.LabelOldFilePath.Wrap(300)
            self.BoardChanged(self.old_board, False)
            self.Layout()
            self.AddToLog("Added old board file")
            self.UpdateCompLayers()

    def UploadNewFile(self, event):
        new_board_path = self.OpenFileDialog()

        if new_board_path:
            self.new_board = PcbBoard(path=new_board_path)

            self.LabelNewFilePath.SetLabelText(new_board_path)
            self.BoardChanged(self.new_board, True)
            self.Layout()
            self.AddToLog("Added new board file")

    # Maybe use some way to make it not specific to the New Board
    def UseCurrentBoard(self, event):
        self.new_board = PcbBoard()

        self.LabelNewFilePath.SetLabelText("Current Board")
        self.BoardChanged(self.new_board, True)
        self.Layout()

    def BoardChanged(self, board, is_new):
        edge_ind = 1 if is_new else 0
        print("new_board_added", board.is_valid)

        if board.is_valid:
            print("new board is valid")
            self.board_vis.PlotBoard(board, "New Board" if is_new else "Old Board")
            
            self.UpdateAlignChoices()
            self.UpdateBoardAlignment()

    def UpdateCompLayers(self):
        self.all_layers = self.old_board.get_layers()

        self.listBoxCompLayers.Clear()

        for layer in self.all_layers:
            self.listBoxCompLayers.Append(layer)

    def ComparisonMethodChanged(self, event):
        choices = ["component", "line", "hybrid"]
        index = self.rbCompMethod.GetSelection()
        self.comparison_method = choices[index]
        self.AddToLog(f"Comparison method changed to {choices[index]}")
    
    def ChangeEdgeSelection(self, event):
        self.Hide()
        selection_result = ComponentSelectionDialog(self).Show()   

    def HandleEdgeSelected(self):
        new_edge_corner = self.new_board.change_edge()
        if new_edge_corner:
            log_message = f"Changed edge, with top left corner at {new_edge_corner}"
        else:
            log_message = "Failed to get edge"

        self.AddToLog(log_message)
        # self.AddToLog(str(self.new_board.edge))

    def AlignMethodChanged(self, event):
        index = self.rbAlignMethod.GetSelection()
        self.align_method= ALIGN_METHOD_CHOICES[index]

        if self.align_method == "None":
            self.choiceAlignCorner.Hide()
            self.choiceNewAlign.Hide()
            self.choiceOldAlign.Hide()

        elif self.align_method == "Edge":
            self.choiceAlignCorner.Show()
            self.choiceNewAlign.Show()
            self.choiceOldAlign.Show()

        elif self.align_method == "Component":
            self.choiceAlignCorner.Hide()
            self.choiceNewAlign.Show()
            self.choiceOldAlign.Show() 

        self.UpdateAlignChoices()
        self.Layout()

    def UpdateAlignChoices(self):
        new_board_choices = []
        old_board_choices = []
        old_selection = self.choiceOldAlign.GetCurrentSelection()
        new_selection = self.choiceNewAlign.GetCurrentSelection()
        self.choiceOldAlign.Clear()
        self.choiceNewAlign.Clear()

        if self.align_method == "None":
            return

        elif self.align_method == "Edge":              
            if self.old_board and self.old_board.is_valid:
                for name, pos, _, _ in self.old_board.edge_cut_shapes:
                    old_board_choices.append(f"{name} at ({pos[0]//IU_PER_MM}, {pos[1]//IU_PER_MM})")

            if self.new_board and self.new_board.is_valid:
                for name, pos, _, _ in self.new_board.edge_cut_shapes:
                    new_board_choices.append(f"{name} at ({pos[0]//IU_PER_MM}, {pos[1]//IU_PER_MM})")

        elif self.align_method == "Component":
            if self.old_board and self.old_board.is_valid:
                for name, pos, _ in self.old_board.footprint_names:
                    old_board_choices.append(f"{name} at ({pos[0]//IU_PER_MM}, {pos[1]//IU_PER_MM})")

            if self.new_board and self.new_board.is_valid:
                for name, pos, _ in self.new_board.footprint_names:
                    new_board_choices.append(f"{name} at ({pos[0]//IU_PER_MM}, {pos[1]//IU_PER_MM})")

        self.choiceOldAlign.AppendItems(old_board_choices)
        self.choiceOldAlign.SetSelection(old_selection)

        self.choiceNewAlign.AppendItems(new_board_choices)
        self.choiceNewAlign.SetSelection(new_selection)

    def UpdateBoardAlignment(self):
        if (not self.old_board) or (not self.new_board):
            return 
        
        if self.align_method == "None":
            self.old_board.reset_offset()
            self.board_vis.ResetBoard("Old Board")
        
        else:
            old_choice_ind = self.choiceOldAlign.GetCurrentSelection()
            new_choice_ind = self.choiceNewAlign.GetCurrentSelection()
            
            print(f"indices for alignment are {old_choice_ind} and {new_choice_ind}")

            if self.align_method == "Edge":
                corner_name = ALIGN_CORNER_CHOICES[self.choiceAlignCorner.GetCurrentSelection()]
                offset_vec = get_offset(self.new_board, self.old_board, 
                                          old_edge_ind=old_choice_ind, new_edge_ind=new_choice_ind, corner_name=corner_name)

            elif self.align_method == "Component":
                offset_vec = get_offset(self.new_board, self.old_board, 
                                          old_component_ind=old_choice_ind, new_component_ind=new_choice_ind)
            
            self.board_vis.OffsetBoard("Old Board", offset_vec)
            self.old_board.offset(offset_vec)
            self.UpdateAlignChoices()
            self.AddToLog("Boards aligned")

    def CompareBoards(self, event):
        # First get the layers selected
        selected_layers = self.listBoxCompLayers.GetSelections()

        if len(selected_layers) < 1:
            return

        # Aligning the boards
        # self.AddToLog("Before aligning " + str(self.new_board.edge.GetStart()))
        # align_boards(self.new_board, self.old_board, corner_name=self.align_corner)
        # self.AddToLog("Boards aligned")
        # self.AddToLog("After aligning " + str(self.new_board.edge.GetStart()))

        #Convert from indexes to layer names
        selected_layers = [self.all_layers[index] for index in selected_layers]

        erase_paths, write_paths = self.new_board.compare_and_plot(self.old_board, selected_layers, compare_paths=self.comparison_method)
        self.AddToLog("Boards compared")
        self.erase_paths = erase_paths
        self.write_paths = write_paths
        self.board_vis.PlotBoard(self.new_board, ERASE_NAME, path_dict=erase_paths)
        self.board_vis.PlotBoard(self.new_board, WRITE_NAME, path_dict=write_paths)
        

    def ExportFiles(self, event):
        self.new_board.export_files()
        self.AddToLog(f"Files exported to {self.new_board.comp_folder_path}")
        pass

    def RunAnalysis(self, event):
        self.comp_dialog = CompAnalysisDialog(self.old_board, self.new_board, self.erase_paths, self.write_paths)
        # self.comp_dialog.ShowModal()
        text = self.comp_dialog.CalcResources()
        self.comp_dialog.Destroy()
        self.AddToLog(text)
        pass

    def OKClicked(self, event):
        self.new_board.open_disp_board()
        self.Close()
        pass


from .poly_comparison import ComponentShape

import numpy as N
# Way to make Y increase downwards
# From https://github.com/wxWidgets/Phoenix/blob/master/samples/floatcanvas/YDownDemo.py
def YDownProjection(CenterPoint):
    return N.array((1,-1))

BACKGROUND_COLOR = "#000020"
BOARD_COLORS = {"Old Board":{"F.Cu":"#DD1010", "B.Cu":"#2f2fad", "Edge.Cuts":"#DDDDDD"},
                "New Board":{"F.Cu":"#fa377b", "B.Cu":"#52b8f2", "Edge.Cuts":"#DDDDDD"},
                ERASE_NAME:{"F.Cu":"#eb4a05", "B.Cu":"#0a8008", "Edge.Cuts":"#DDDDDD"},
                WRITE_NAME:{"F.Cu":"#ffc021", "B.Cu":"#0bd439", "Edge.Cuts":"#DDDDDD"}}

board_disp_order = ["New Board", "Old Board", WRITE_NAME, ERASE_NAME]
layer_disp_order = ["F.Cu", "B.Cu", "Edge.Cuts"]

class BoardVisPanel(wx.Panel):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.CanvasSetup()
        self.boards = dict()

    def CanvasSetup(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        nc = NavCanvas.NavCanvas(self, ProjectionFun=YDownProjection, Debug=0, BackgroundColor=BACKGROUND_COLOR)
        # nc = FloatCanvas.FloatCanvas(self, ProjectionFun=None, Debug=0, BackgroundColor="#000020")
        sizer.Add(nc, 1, wx.EXPAND | wx.ALL, 5)
        self.canvas = nc.Canvas
        
        toolbar = nc.ToolBar
        toolbar.AddSeparator()
        self.coords_text = wx.StaticText(toolbar)
        toolbar.AddControl(self.coords_text)
        toolbar.Realize()
        # sizer.Add(self.coords_text,0)

        # button = wx.Button(self, wx.ID_ANY, "test")
        # sizer.Add(button)
        # button.Bind(wx.EVT_BUTTON, self.testing)
        # self.rect = self.canvas.AddRectangle((0,0),(100,100),LineColor="#DDDDDD")

        self.layer_control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.layer_control_sizer)
        self.board_properties = dict()
        
        self.canvas.Bind(FloatCanvas.EVT_MOTION, self.OnMove)

        self.canvas.Draw(True)
        self.canvas.ZoomToBB()
        # self.Layout()

    def ResetBoard(self, board_name):
        if not (board_name in self.board_properties):
            return
        
        if "offset" in self.board_properties[board_name]:
            self.OffsetBoard(board_name, -self.board_properties[board_name]["offset"])

    def OffsetBoard(self, board_name, vector):
        if not ("offset" in self.board_properties[board_name]):
            self.board_properties[board_name]["offset"] = vector
        else:
            self.board_properties[board_name]["offset"] += vector

        for layer in self.boards[board_name]:
            for shape in self.boards[board_name][layer]:
                shape.Move(vector)

        self.canvas.ZoomToBB()
        self.canvas.Draw(True)

    def PlotBoard(self, board, board_name, net_dict=None, path_dict=None):
        print("plotting board")
        if board_name in self.boards:
            self.RemoveBoard(board_name=board_name)
            self.boards.pop(board_name, None) # Is probably redundant

        if not board:
            return

        self.board_properties[board_name] = dict()
        self.boards[board_name] = dict()

        if not net_dict:
            net_dict = board.net_dict

        if not path_dict:
            for layer in net_dict:
                self.boards[board_name][layer] = []
                for net in net_dict[layer]:
                    for pad in net.pad_lst:
                        if len(pad.poly_points) == 0:
                            break
                        pad_shape = self.canvas.AddPolygon(pad.poly_points, LineStyle="Transparent", 
                                                           FillStyle="Solid", FillColor=BOARD_COLORS[board_name][layer])
                        self.boards[board_name][layer].append(pad_shape)

                    for track in net.track_lst:
                        shape = ComponentShape(track, "track")
                        point_lst = shape.outline.exterior.coords
                        if len(point_lst) == 0:
                            break
                        track_shape = self.canvas.AddPolygon(point_lst, LineStyle="Transparent", 
                                                             FillStyle="Solid", FillColor=BOARD_COLORS[board_name][layer])
                        self.boards[board_name][layer].append(track_shape)

        else:
            for layer in path_dict:
                self.boards[board_name][layer] = []
                path = path_dict[layer]
                polygons = path.get_poly_list()
                for polygon in polygons:
                    ext_point_lst = polygon.exterior.coords
                    if len(ext_point_lst) == 0:
                            break
                    shape = self.canvas.AddPolygon(ext_point_lst, LineStyle="Transparent", FillStyle="Solid", FillColor=BOARD_COLORS[board_name][layer])
                    self.boards[board_name][layer].append(shape)

                    # As far as I know, you cannot natively add holes into polygons
                    # So I'm going to plot the holes as polygons with the same color as the background
                    # Might be worth looking into if simply appending the hole points to the exterior points
                    # Will create a hole
                    for hole in polygon.interiors:
                        if len(hole.coords) == 0:
                            break
                        hole_shape = self.canvas.AddPolygon(hole.coords, LineStyle="Transparent", FillStyle="Solid", FillColor=BACKGROUND_COLOR)
                        self.boards[board_name][layer].append(hole_shape)
       
        self.boards[board_name]["Edge.Cuts"] = []
        for shape_name, start, end, _ in board.edge_cut_shapes:
            if shape_name == "Rect":
                width = end[0] - start[0]
                height = end[1] - start[1]
                shape = self.canvas.AddRectangle(start, (width, height), LineColor="#DDDDDD", FillStyle="Transparent")
            elif shape_name == "Circle":
                diameter = 2 * (end - start).EuclideanNorm()
                shape = self.canvas.AddCircle(start, diameter, LineColor="#DDDDDD", FillStyle="Transparent")
            else:
                print(f"Unkown Shape: {shape_name} at {start}")
                pass
            self.boards[board_name]["Edge.Cuts"].append(shape)

        self.AddBoardLayerControls(board_name)
        self.SetDisplayOrder()
        self.canvas.Draw(True)
        self.canvas.ZoomToBB()

    def RemoveBoard(self, board_name):
        # if board_name in 
        if board_name in self.boards:
            board_geometry = self.boards[board_name]
            for layer in board_geometry:
                self.canvas.RemoveObjects(board_geometry[layer])

            self.RemovedBoardLayerControls(board_name)

    def RemovedBoardLayerControls(self, board_name):
        self.layer_control_sizer.Remove(self.board_properties[board_name]["layer sizer"])
        self.Layout()

    def AddBoardLayerControls(self, board_name):
        check_box_container = wx.StaticBoxSizer(wx.VERTICAL, self, board_name)
        self.board_properties[board_name]["layer sizer"] = check_box_container
        self.layer_control_sizer.Add(check_box_container, 1, wx.EXPAND | wx.ALL, 5)

        for layer in self.boards[board_name]:
            cb_sizer = wx.BoxSizer(wx.HORIZONTAL)
            color_circle = wx.StaticText(self, label="⬤ ")
            color_circle.SetForegroundColour(BOARD_COLORS[board_name][layer])
            check_box = wx.CheckBox(self, wx.ID_ANY, layer)
            check_box.SetValue(True)
            cb_sizer.Add(check_box)
            cb_sizer.Add(color_circle)
            layer_change_function = \
                lambda event, cb=check_box, l=layer: self.ChangeLayerVisibility(board_name, l, cb.IsChecked())
            check_box.Bind(wx.EVT_CHECKBOX, layer_change_function)
            check_box_container.Add(cb_sizer)

        self.Layout()

    def SetDisplayOrder(self):
        for board in reversed(board_disp_order):
            if board in self.boards:
                for layer in reversed(layer_disp_order):
                    if layer in self.boards[board]:
                        for component in self.boards[board][layer]:
                            
                            component.PutInForeground()
                            component.PutInBackground()
                            pass
        self.canvas.Draw(True)

    # If layer name is None, then hides entire board
    def ChangeLayerVisibility(self, board_name, layer_name=None, show=False):
        print(f"showing={show} {layer_name} in {board_name}")
        if not layer_name:
            layer_list = self.boards[board_name].keys()
        else:
            layer_list = [layer_name]

        for layer in layer_list:
            for component in self.boards[board_name][layer]:
                if show:
                    component.Show()
                else:
                    component.Hide()

        self.canvas.Draw(True)

    # From https://github.com/wxWidgets/Phoenix/blob/master/samples/floatcanvas/DrawRect.py
    # But slightly edited
    def OnMove(self, event):
        """
        Updates the status bar with the world coordinates

        """
        coords_in_mm = (event.Coords[0]/IU_PER_MM, event.Coords[1]/IU_PER_MM)
        self.coords_text.SetLabel("%.4f, %.4f"%coords_in_mm)
        event.Skip()

