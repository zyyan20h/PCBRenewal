import pcbnew
from .point_graphing import point_grapher as pg
from .pcb_file_management import OpenFileDialog
from .pcb_components import PcbTrackList , PcbPadList, PcbBoard

# REMOVE
import matplotlib.pyplot as plt

#TODO RENAME!!!
class ComplexPluginAction(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Track Subtractor"
        self.category = "A descriptive category name"
        self.description = "Sets the position of a track to the center for absolutely no reason"
        self.show_toolbar_button = True # Optional, defaults to False
        #self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png') # Optional

    def Run(self):
        # The entry function of the plugin that is executed on user action
        
        # new_board_ref = pcbnew.LoadBoard(r"D:\KiCad\PCBS\test2\test2.kicad_pcb")

        old_file_name = OpenFileDialog()

        new_board_ref = pcbnew.GetBoard()
        # new_board_ref = pcbnew.LoadBoard(r"D:\KiCad\PCBS\renewablePCB\KiCAD_designs\bristleBot_V2\bristleBot_V2.kicad_pcb")

        # pfd = PcbFileDialog()
             
        # path = pfd.openFileWindow()
        
        # board2 = pcbnew.LoadBoard(path)
        # board2 = board1

        old_board_ref = pcbnew.LoadBoard(old_file_name)
        # old_board_ref = pcbnew.LoadBoard(r"D:\KiCad\PCBS\renewablePCB\KiCAD_designs\bristleBot\bristleBot.kicad_pcb")
        # old_board_ref = pcbnew.LoadBoard(r"D:\KiCad\PCBS\test1\test1.kicad_pcb")
        
        # print(f"board ref {pcbnew.GetBoard()}")

        new_board = PcbBoard(new_board_ref)
        old_board = PcbBoard(old_board_ref)

        new_board.compare_and_plot(old_board)

        # new_ptl = PcbTrackList()
        # new_ptl.add_to_list(new_board_ref)

        # new_ppl = PcbPadList()
        # new_ppl.add_to_list(new_board_ref)
        # # print(f"new t {list(map(str, new_ptl.front_track_list))}")
        
        # old_ptl = PcbTrackList()
        # old_ptl.add_to_list(old_board_ref)
        # # print(f"old t {old_ptl.front_track_list}")
        
        # erase_track_lst, write_track_lst = new_ptl.compare_tracks(old_ptl)
        
        # print(f"erase {erase_track_lst.front_track_list}")
        # print(f"write {write_track_lst.front_track_list}")

        # # Plotting tracks to be erased
        # erase_track_lst.plot_in_kicad(new_board_ref, pcbnew.User_1, pcbnew.User_2)

        # # Plotting tracks to be written
        # write_track_lst.plot_in_kicad(new_board_ref, pcbnew.User_3, pcbnew.User_4)

        # t_lists = [ptl1, ptl2] + list(ekw_tuple)

        # #pg.set_fig_name("Test")
        # #t_lists[4].graph_lists()

        # # pg.set_fig_name("Old Board")
        # axis = plt.subplot(231)
        # #axis.invert_yaxis()
        # axis.title.set_text("Old Board")
        # pg.adjust_axes(axis)
        # ptl1.graph_lists(axes= axis)

        # # pg.set_fig_name("New Board")
        # axis = plt.subplot(232)
        # # axis.invert_yaxis()
        # axis.title.set_text("New Board")
        # pg.adjust_axes(axis)
        # ptl2.graph_lists(axes= axis)
        
        # # pg.set_fig_name("Erase")
        # axis = plt.subplot(234)
        # # axis.invert_yaxis()
        # axis.title.set_text("Erase")
        # pg.adjust_axes(axis)
        # ekw_tuple[0].graph_lists(axes= axis)

        # # pg.set_fig_name("Keep")
        # axis = plt.subplot(235)
        # # axis.invert_yaxis()
        # axis.title.set_text("Keep")
        # pg.adjust_axes(axis)
        # ekw_tuple[1].graph_lists(axes= axis)

        # # pg.set_fig_name("Write")
        # axis = plt.subplot(236)
        # # axis.invert_yaxis()
        # axis.title.set_text("Write")
        # pg.adjust_axes(axis)
        # ekw_tuple[2].graph_lists(axes= axis)

        # plt.tight_layout()
        # plt.show()

        pcbnew.Refresh()
