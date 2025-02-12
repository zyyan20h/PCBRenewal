import pcbnew
from .comparison_dialog_events import BoardComparisonWindow
from .pcb_components import PcbBoard
import wx

class RenewalPluginAction(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "PCB Renewal"
        self.category = "A descriptive category name"
        self.description = "Compares two boards"
        self.show_toolbar_button = True # Optional, defaults to False

    def Run(self):
        app = wx.App()
        bcw = BoardComparisonWindow()
        bcw.Show()
        app.MainLoop()

        pcbnew.Refresh()
