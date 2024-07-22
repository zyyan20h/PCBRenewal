# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.0.0-0-g0efcecf)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class ComparisonOptionsDialog
###########################################################################

class ComparisonOptionsDialog ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Compare Boards", pos = wx.DefaultPosition, size = wx.Size( 714,814 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer6 = wx.BoxSizer( wx.VERTICAL )

		self.PanelAll = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer4 = wx.BoxSizer( wx.VERTICAL )

		sbSizerOldFile = wx.StaticBoxSizer( wx.StaticBox( self.PanelAll, wx.ID_ANY, u"Old Board" ), wx.VERTICAL )

		self.PanelOldFileUpload = wx.Panel( sbSizerOldFile.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer7 = wx.BoxSizer( wx.HORIZONTAL )

		self.LabelOldFilePath = wx.StaticText( self.PanelOldFileUpload, wx.ID_ANY, u"*File Not Selected*", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.LabelOldFilePath.SetLabelMarkup( u"*File Not Selected*" )
		self.LabelOldFilePath.Wrap( -1 )

		self.LabelOldFilePath.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )

		bSizer7.Add( self.LabelOldFilePath, 9, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.ButtonOldFileUpload = wx.Button( self.PanelOldFileUpload, wx.ID_ANY, u"Select File", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer7.Add( self.ButtonOldFileUpload, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		self.PanelOldFileUpload.SetSizer( bSizer7 )
		self.PanelOldFileUpload.Layout()
		bSizer7.Fit( self.PanelOldFileUpload )
		sbSizerOldFile.Add( self.PanelOldFileUpload, 1, wx.EXPAND |wx.ALL, 5 )


		bSizer4.Add( sbSizerOldFile, 1, wx.EXPAND, 5 )

		sbSizerNewFile = wx.StaticBoxSizer( wx.StaticBox( self.PanelAll, wx.ID_ANY, u"New Board" ), wx.VERTICAL )

		self.PanelNewFileUpload = wx.Panel( sbSizerNewFile.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

		self.LabelNewFilePath = wx.StaticText( self.PanelNewFileUpload, wx.ID_ANY, u"*File Not Selected*", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.LabelNewFilePath.Wrap( -1 )

		self.LabelNewFilePath.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )

		bSizer9.Add( self.LabelNewFilePath, 9, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.ButtonNewFileUpload = wx.Button( self.PanelNewFileUpload, wx.ID_ANY, u"Select File", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.ButtonNewFileUpload, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.ButtonUseCurrBoard = wx.Button( self.PanelNewFileUpload, wx.ID_ANY, u"Use Current Board", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.ButtonUseCurrBoard, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		self.PanelNewFileUpload.SetSizer( bSizer9 )
		self.PanelNewFileUpload.Layout()
		bSizer9.Fit( self.PanelNewFileUpload )
		sbSizerNewFile.Add( self.PanelNewFileUpload, 1, wx.EXPAND |wx.ALL, 5 )


		bSizer4.Add( sbSizerNewFile, 1, wx.EXPAND, 5 )

		sbSizerAlignBoards = wx.StaticBoxSizer( wx.StaticBox( self.PanelAll, wx.ID_ANY, u"Align Boards" ), wx.VERTICAL )

		bSizer71 = wx.BoxSizer( wx.VERTICAL )

		self.buttonSelectEdges = wx.Button( sbSizerAlignBoards.GetStaticBox(), wx.ID_ANY, u"Select Edge Cut", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer71.Add( self.buttonSelectEdges, 0, wx.ALL, 5 )

		rbAlignCornerChoices = [ u"Top Left", u"Bottom Left", u"Top Right", u"Bottom Right" ]
		self.rbAlignCorner = wx.RadioBox( sbSizerAlignBoards.GetStaticBox(), wx.ID_ANY, u"Pick a corner", wx.DefaultPosition, wx.DefaultSize, rbAlignCornerChoices, 2, wx.RA_SPECIFY_ROWS )
		self.rbAlignCorner.SetSelection( 0 )
		bSizer71.Add( self.rbAlignCorner, 0, wx.ALL, 5 )


		sbSizerAlignBoards.Add( bSizer71, 1, wx.EXPAND, 5 )


		bSizer4.Add( sbSizerAlignBoards, 1, wx.EXPAND, 5 )

		bSizer10 = wx.BoxSizer( wx.HORIZONTAL )

		sbSizerCompLayers = wx.StaticBoxSizer( wx.StaticBox( self.PanelAll, wx.ID_ANY, u"Layers to Compare" ), wx.VERTICAL )

		self.PanelCompLayers = wx.Panel( sbSizerCompLayers.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.PanelCompLayers.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

		bSizer2 = wx.BoxSizer( wx.VERTICAL )

		listBoxCompLayersChoices = []
		self.listBoxCompLayers = wx.ListBox( self.PanelCompLayers, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, listBoxCompLayersChoices, wx.LB_MULTIPLE )
		bSizer2.Add( self.listBoxCompLayers, 1, wx.ALL|wx.EXPAND, 5 )

		rbCompMethodChoices = [ u"Component", u"Line", u"Hybrid" ]
		self.rbCompMethod = wx.RadioBox( self.PanelCompLayers, wx.ID_ANY, u"Comparison Method", wx.DefaultPosition, wx.DefaultSize, rbCompMethodChoices, 1, wx.RA_SPECIFY_COLS )
		self.rbCompMethod.SetSelection( 0 )
		bSizer2.Add( self.rbCompMethod, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

		self.ButtonCompare = wx.Button( self.PanelCompLayers, wx.ID_ANY, u"Compare", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.ButtonCompare, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )


		self.PanelCompLayers.SetSizer( bSizer2 )
		self.PanelCompLayers.Layout()
		bSizer2.Fit( self.PanelCompLayers )
		sbSizerCompLayers.Add( self.PanelCompLayers, 1, wx.EXPAND|wx.ALL, 5 )


		bSizer10.Add( sbSizerCompLayers, 5, wx.EXPAND, 5 )


		bSizer10.Add( ( 10, 0), 0, wx.EXPAND, 5 )

		sbSizerExportFiles = wx.StaticBoxSizer( wx.StaticBox( self.PanelAll, wx.ID_ANY, u"Export Files" ), wx.VERTICAL )

		self.PanelExportFiles = wx.ScrolledWindow( sbSizerExportFiles.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.PanelExportFiles.SetScrollRate( 5, 5 )
		sbSizerExportFiles.Add( self.PanelExportFiles, 1, wx.ALL|wx.EXPAND, 5 )

		self.ButtonExportFiles = wx.Button( sbSizerExportFiles.GetStaticBox(), wx.ID_ANY, u"Export", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizerExportFiles.Add( self.ButtonExportFiles, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )


		bSizer10.Add( sbSizerExportFiles, 5, wx.EXPAND, 5 )


		bSizer4.Add( bSizer10, 10, wx.EXPAND, 5 )

		self.PanelLog = wx.ScrolledWindow( self.PanelAll, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.PanelLog.SetScrollRate( 5, 5 )
		self.PanelLog.SetMinSize( wx.Size( 75,75 ) )

		bSizer4.Add( self.PanelLog, 0, wx.ALL|wx.EXPAND, 5 )

		self.ButtonOK = wx.Button( self.PanelAll, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( self.ButtonOK, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )


		self.PanelAll.SetSizer( bSizer4 )
		self.PanelAll.Layout()
		bSizer4.Fit( self.PanelAll )
		bSizer6.Add( self.PanelAll, 1, wx.EXPAND |wx.ALL, 10 )


		self.SetSizer( bSizer6 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_INIT_DIALOG, self.DialogInit )
		self.ButtonOldFileUpload.Bind( wx.EVT_BUTTON, self.UploadOldFile )
		self.ButtonNewFileUpload.Bind( wx.EVT_BUTTON, self.UploadNewFile )
		self.ButtonUseCurrBoard.Bind( wx.EVT_BUTTON, self.UseCurrentBoard )
		self.buttonSelectEdges.Bind( wx.EVT_BUTTON, self.ChangeEdgeSelection )
		self.rbAlignCorner.Bind( wx.EVT_RADIOBOX, self.AlignCornerChanged )
		self.rbCompMethod.Bind( wx.EVT_RADIOBOX, self.ComparisonMethodChanged )
		self.ButtonCompare.Bind( wx.EVT_BUTTON, self.CompareBoards )
		self.ButtonExportFiles.Bind( wx.EVT_BUTTON, self.ExportFiles )
		self.ButtonOK.Bind( wx.EVT_BUTTON, self.OKClicked )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def DialogInit( self, event ):
		event.Skip()

	def UploadOldFile( self, event ):
		event.Skip()

	def UploadNewFile( self, event ):
		event.Skip()

	def UseCurrentBoard( self, event ):
		event.Skip()

	def ChangeEdgeSelection( self, event ):
		event.Skip()

	def AlignCornerChanged( self, event ):
		event.Skip()

	def ComparisonMethodChanged( self, event ):
		event.Skip()

	def CompareBoards( self, event ):
		event.Skip()

	def ExportFiles( self, event ):
		event.Skip()

	def OKClicked( self, event ):
		event.Skip()


