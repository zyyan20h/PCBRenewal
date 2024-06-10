import pcbnew
from .comparison_dialog_events import BoardComparisonWindow
from .pcb_components import PcbBoard
import wx

# REMOVE
# import matplotlib.pyplot as plt

#TODO RENAME!!!
class ComplexPluginAction(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Track Subtractor"
        self.category = "A descriptive category name"
        self.description = "Compares two boards"
        self.show_toolbar_button = True # Optional, defaults to False
        #self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png') # Optional

    def Run(self):
        # The entry function of the plugin that is executed on user action
        
        # new_board_ref = pcbnew.LoadBoard(r"D:\KiCad\PCBS\test2\test2.kicad_pcb")

        # app = wx.App()
        bcw = BoardComparisonWindow()
        bcw.ShowModal()
        bcw.Destroy()
        # del app

        # # If you cancel while choosing a file
        # if not bcw.old_board_path:
        #     return

        # old_board_ref = pcbnew.LoadBoard(bcw.old_board_path)

        # new_board_ref = pcbnew.GetBoard()

        # # new_board_ref = pcbnew.LoadBoard(r"D:\KiCad\PCBS\renewablePCB\KiCAD_designs\bristleBot_V2\bristleBot_V2.kicad_pcb")

        # # old_board_ref = pcbnew.LoadBoard(r"D:\KiCad\PCBS\renewablePCB\KiCAD_designs\bristleBot\bristleBot.kicad_pcb")
        # # old_board_ref = pcbnew.LoadBoard(r"D:\KiCad\PCBS\test1\test1.kicad_pcb")

        # new_board = PcbBoard(new_board_ref)
        # old_board = PcbBoard(old_board_ref)

        # new_board.compare_and_plot(old_board)

        pcbnew.Refresh()
