import wx
from wx.lib.floatcanvas import NavCanvas, FloatCanvas
# import wx.svg
from .comparison_dialog_ui import ComparisonOptionsDialog
from .pcb_components import PcbBoard, align_boards
from .selection_dialog_events import ComponentSelectionDialog

# TODO Maybe call layout locally instead of self.layout everywhere

class BoardComparisonWindow(ComparisonOptionsDialog):

    def __init__(self):
        super(BoardComparisonWindow, self).__init__(None)

        self.old_board_path = None
        self.old_board = None
        self.new_board = None
        self.align_corner = "topleft"
        self.comparison_method = "component"
        self.export_data = []
        self.log_sizer = None

    def DialogInit(self, event):
        sizer = self.PanelOperations.GetSizer()
        self.board_vis = BoardVisPanel( self.PanelOperations, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        sizer.Add(self.board_vis, 2, wx.EXPAND | wx.ALL, 5)

        self.UseCurrentBoard(None)
        self.Layout()

        if not self.log_sizer:
            self.log_sizer = wx.BoxSizer(wx.VERTICAL)
            self.PanelLog.SetSizer(self.log_sizer)
            # self.AddToLog("Dialog init!")
        pass

    def OnClose(self, event):
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
        # if self.board_edges[edge_ind]:
        # self.AlignCanvas.ClearAll()
        print("new_board_added", board.is_valid)

        if board.is_valid:
            print("new board is valid")
            # board_start = board.edge.GetStart()
            # board_end = board.edge.GetEnd()
            # width = (board_end[0] - board_start[0]) 
            # height = (board_end[1] - board_start[1]) 
            # self.board_edges[edge_ind] = self.AlignCanvas.AddRectangle(board_start, (width, height), LineColor="#DDDDDD")

            # self.AlignCanvas.Draw()
            # self.AlignCanvas.ZoomToBB()
            self.board_vis.PlotBoard(board, "New Board" if is_new else "Old Board")

    def UpdateCompLayers(self):


        self.all_layers = self.old_board.get_layers()

        # all_layers = ["1","2","3","4"]

        # b = PcbBoard(board=None, path=self.OpenFileDialog())
        # all_layers = b.get_layers()

        # layer_sizer = self.PanelCompLayers.GetSizer()
        # layer_sizer = wx.BoxSizer(orient=wx.VERTICAL)
        
        self.listBoxCompLayers.Clear()

        for layer in self.all_layers:
            # new_cb = wx.CheckBox(self.PanelCompLayers, wx.ID_ANY, layer, wx.DefaultPosition, wx.DefaultSize, 0)
            # layer_sizer.Add(new_cb, 1, wx.ALL, 5)

            self.listBoxCompLayers.Append(layer)

        # self.PanelCompLayers.SetSizer(layer_sizer)

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

    def AlignCornerChanged(self, event):
        choices = ["topleft", "bottomleft", "topright", "bottomright"]
        index = self.rbAlignCorner.GetSelection()
        self.align_corner = choices[index]

    def CompareBoards(self, event):
        # First get the layers selected
        selected_layers = self.listBoxCompLayers.GetSelections()

        if len(selected_layers) < 1:
            return

        self.PanelExportFiles.DestroyChildren()

        # Aligning the boards
        # self.AddToLog("Before aligning " + str(self.new_board.edge.GetStart()))
        align_boards(self.new_board, self.old_board, corner_name=self.align_corner)
        self.AddToLog("Boards aligned")
        # self.AddToLog("After aligning " + str(self.new_board.edge.GetStart()))

        #Convert from indexes to layer names
        selected_layers = [self.all_layers[index] for index in selected_layers]

        erase_paths, write_paths = self.new_board.compare_and_plot(self.old_board, selected_layers, compare_paths=self.comparison_method)
        self.AddToLog("Boards compared")

        self.board_vis.PlotBoard(self.new_board, "Stuff to be Erased", path_dict=erase_paths)
        self.board_vis.PlotBoard(self.new_board, "Stuff to be Written", path_dict=write_paths)
        

    def ExportFiles(self, event):

        # file_names = []

        # # Getting the files that are checked to export
        # for layer in self.export_data:
        #     if layer["checkbox"].IsChecked():
        #         file_names.append((layer["textctrl"].GetValue(), layer["id"]))

        self.new_board.export_files()
        self.AddToLog(f"Files exported to {self.new_board.comp_folder_path}")
        pass

    def OKClicked(self, event):
        # Making sure a file has been selected
        # if self.old_board_path != None:
        #     self.EndModal(wx.ID_OK)
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

        # button = wx.Button(self, wx.ID_ANY, "test")
        # sizer.Add(button)
        # button.Bind(wx.EVT_BUTTON, self.testing)
        # self.rect = self.canvas.AddRectangle((0,0),(100,100),LineColor="#DDDDDD")

        self.layer_control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.layer_control_sizer)
        self.board_properties = dict()
        
        self.canvas.Draw(True)
        self.canvas.ZoomToBB()
        # self.Layout()

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
                        pad_shape = self.canvas.AddPolygon(pad.poly_points, LineStyle="Transparent", FillStyle="Solid", FillColor="#DD1010")
                        self.boards[board_name][layer].append(pad_shape)

                    for track in net.track_lst:
                        shape = ComponentShape(track, "track")
                        point_lst = shape.outline.exterior.coords
                        # track_shape = self.canvas.AddLine((track.start, track.end), LineColor="#DD1010")
                        track_shape = self.canvas.AddPolygon(point_lst, LineStyle="Transparent", FillStyle="Solid", FillColor="#DD1010")
                        self.boards[board_name][layer].append(track_shape)

        else:
            for layer in path_dict:
                self.boards[board_name][layer] = []
                path = path_dict[layer]
                polygons = path.get_poly_list()
                for polygon in polygons:
                    ext_point_lst = polygon.exterior.coords
                    shape = self.canvas.AddPolygon(ext_point_lst, LineStyle="Transparent", FillStyle="Solid", FillColor="#32a852")
                    self.boards[board_name][layer].append(shape)

                    # As far as I know, you cannot natively add holes into polygons
                    # So I'm going to plot the holes as polygons with the same color as the background
                    # Might be worth looking into if simply appending the hole points to the exterior points
                    # Will create a hole
                    for hole in polygon.interiors:
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
            check_box = wx.CheckBox(self, wx.ID_ANY, layer)
            check_box.SetValue(True)
            layer_change_function = \
                lambda event, cb=check_box, l=layer: self.ChangeLayerVisibility(board_name, l, cb.IsChecked())
            check_box.Bind(wx.EVT_CHECKBOX, layer_change_function)
            check_box_container.Add(check_box)

        self.Layout()

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

