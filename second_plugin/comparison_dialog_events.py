import wx
import wx.lib.scrolledpanel
# import wx.svg
from .comparison_dialog_ui import ComparisonOptionsDialog
from .pcb_components import PcbBoard, align_boards

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

    def DialogInit(self, event):
        
        # layer_sizer = self.PanelCompLayers.GetSizer()

        # new_cb = wx.CheckBox(self.PanelCompLayers, wx.ID_ANY, u"Test", wx.DefaultPosition, wx.DefaultSize,)
        # layer_sizer.Add(new_cb)

        # all_layers = ["1", "22", "333", "4444","1", "22", "333", "4444","1", "22", "333", "4444","1", "22", "333", "4444","1", "22", "333", "4444","1", "22", "333", "4444","1", "22", "333", "4444","1", "22", "333", "4444"]

        # layer_sizer = wx.BoxSizer(orient=wx.VERTICAL)
        

        # for layer in all_layers:
        #     new_cb = wx.CheckBox(self.PanelCompLayers, wx.ID_ANY, layer, wx.DefaultPosition, wx.DefaultSize, 0)
        #     layer_sizer.Add(new_cb, 1, wx.ALL, 5)

        # self.PanelCompLayers.SetSizer(layer_sizer)

        # self.UpdateCompLayers()
        # self.UploadOldFile(event=None)
        # raise Exception("FUCK")
        # self.CompareBoards("AAA)

        self.UseCurrentBoard(None)
        self.log_sizer = wx.BoxSizer(wx.VERTICAL)
        self.PanelLog.SetSizer(self.log_sizer)

        pass
    
    def AddToLog(self, log_text):
        new_label = wx.StaticText(self.PanelLog, label=log_text)
        self.log_sizer.Add(new_label)
        self.PanelLog.Layout()

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
            self.Layout()
            self.AddToLog("Added old board file")
            self.UpdateCompLayers()

    def UploadNewFile(self, event):
        new_board_path = self.OpenFileDialog()

        if new_board_path:
            self.new_board = PcbBoard(path=new_board_path)

            self.LabelNewFilePath.SetLabelText(new_board_path)

            self.Layout()
            self.AddToLog("Added new board file")

    # Maybe use some way to make it not specific to the New Board
    def UseCurrentBoard(self, event):
        self.new_board = PcbBoard()

        self.LabelNewFilePath.SetLabelText("Current Board")

        self.Layout()

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
        align_boards(self.new_board, self.old_board, corner_name=self.align_corner)

        #Convert from indexes to layer names
        selected_layers = [self.all_layers[index] for index in selected_layers]

        layer_pngs = self.new_board.compare_and_plot(self.old_board, selected_layers, compare_paths=self.comparison_method)
        self.AddToLog("Boards compared")
        if not layer_pngs:
            return
        
        # self.AddToLog("Boards compared")

        export_modes_sizer = wx.BoxSizer(wx.VERTICAL)

        for mode in layer_pngs.keys():

            export_files_sizer = wx.StaticBoxSizer( wx.StaticBox( self.PanelExportFiles, wx.ID_ANY, mode ), wx.VERTICAL )

            layer_ind = 0
            for layer_name, file_name, layer_id in layer_pngs[mode]:
                single_file_sizer = wx.BoxSizer(wx.HORIZONTAL)

                new_text_ctrl = wx.TextCtrl(self.PanelExportFiles, wx.ID_ANY, file_name, wx.DefaultPosition, wx.DefaultSize, 0)
                new_check_box = wx.CheckBox(self.PanelExportFiles, wx.ID_ANY, layer_name , wx.DefaultPosition, wx.DefaultSize, 0)
                new_check_box.SetValue(True)


                layer_ind += 1
                
                self.export_data.append({"checkbox" : new_check_box, 
                                        "textctrl" : new_text_ctrl,
                                        "id"       : layer_id})

                single_file_sizer.Add(new_check_box, 1, wx.ALL, 5)
                single_file_sizer.Add(new_text_ctrl)
                single_file_sizer.Add(wx.StaticText(self.PanelExportFiles, wx.ID_ANY,".gbr", style=wx.ALIGN_BOTTOM))
                # single_file_sizer.Add(layer_image)

                export_files_sizer.Add(single_file_sizer, 1, wx.ALL, 5)

            export_modes_sizer.Add(export_files_sizer, 1, wx.ALL, 5)

        self.PanelExportFiles.SetSizer(export_modes_sizer)
        # self.PanelExportFiles.SetupScrolling()

        # Update UI function
        self.Layout()
        self.PanelExportFiles.Layout()

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
        self.EndModal(wx.ID_OK)
        pass
