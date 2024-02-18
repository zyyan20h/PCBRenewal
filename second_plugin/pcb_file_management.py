# import wx
from tkinter.filedialog import askopenfilename

# class PcbFileDialog():
#     def __init__(self) -> None:
#         self.app = wx.App()
#         self.frm = wx.Frame(None, title="Input File")
    
#     def showWindow(self):
#         # Show it.
#         self.frm.Show()

#         # Start the event loop.
#         self.app.MainLoop()

#     def openFileWindow(self):
#         ofd = wx.FileDialog(self.frm, "Open", wildcard = "KiCad PCB files (*.kicad_pcb)|*.kicad_pcb", style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

#         if ofd.ShowModal() == wx.ID_CANCEL :
#             return
        
#         pathname = ofd.GetPath()

#         return pathname

def OpenFileDialog():
    return askopenfilename()

