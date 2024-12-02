import pcbnew
from .comparison_dialog_events import BoardComparisonWindow
from .pcb_components import PcbBoard
import wx

# REMOVE
# import matplotlib.pyplot as plt

#TODO RENAME!!!
class ComplexPluginAction(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "PCB Renewal"
        self.category = "A descriptive category name"
        self.description = "Compares two boards"
        self.show_toolbar_button = True # Optional, defaults to False
        #self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png') # Optional

    def Run(self):
        # The entry function of the plugin that is executed on user action
        
        # new_board_ref = pcbnew.LoadBoard(r"D:\KiCad\PCBS\test2\test2.kicad_pcb")

        app = wx.App()
        bcw = BoardComparisonWindow()
        bcw.Show()
        app.MainLoop()
        # bcw.Destroy()
        # del app
        print("end of program")

        pcbnew.Refresh()
