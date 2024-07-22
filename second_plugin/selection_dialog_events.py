import wx
from .selection_dialog_ui import SelectionWindow

class ComponentSelectionDialog(SelectionWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def CancelSelection(self, event):
        self.Close()

    def DialogClosed(self, event):
        self.parent.Show()
        self.Destroy()
    
    def ComponentSelected(self, event):
        self.parent.HandleEdgeSelected()
        self.Close()