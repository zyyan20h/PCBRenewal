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
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Compare Boards", pos = wx.DefaultPosition, size = wx.Size( 1342,747 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer6 = wx.BoxSizer( wx.VERTICAL )

		self.PanelAll = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer14 = wx.BoxSizer( wx.VERTICAL )

		self.PanelFeatures = wx.Panel( self.PanelAll, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer22 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer4 = wx.BoxSizer( wx.VERTICAL )

		sbSizerOldFile = wx.StaticBoxSizer( wx.StaticBox( self.PanelFeatures, wx.ID_ANY, u"Old Board" ), wx.VERTICAL )

		self.PanelOldFileUpload = wx.Panel( sbSizerOldFile.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer7 = wx.BoxSizer( wx.HORIZONTAL )

		self.LabelOldFilePath = wx.StaticText( self.PanelOldFileUpload, wx.ID_ANY, u"*File Not Selected*", wx.DefaultPosition, wx.DefaultSize, wx.ST_ELLIPSIZE_START|wx.ST_NO_AUTORESIZE )
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


		bSizer4.Add( sbSizerOldFile, 0, wx.EXPAND, 5 )

		sbSizerNewFile = wx.StaticBoxSizer( wx.StaticBox( self.PanelFeatures, wx.ID_ANY, u"New Board" ), wx.VERTICAL )

		self.PanelNewFileUpload = wx.Panel( sbSizerNewFile.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

		self.LabelNewFilePath = wx.StaticText( self.PanelNewFileUpload, wx.ID_ANY, u"*File Not Selected*", wx.DefaultPosition, wx.DefaultSize, wx.ST_ELLIPSIZE_START|wx.ST_NO_AUTORESIZE )
		self.LabelNewFilePath.Wrap( -1 )

		self.LabelNewFilePath.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )

		bSizer9.Add( self.LabelNewFilePath, 9, wx.ALL, 5 )

		self.ButtonUseCurrBoard = wx.Button( self.PanelNewFileUpload, wx.ID_ANY, u"Use Current Board", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.ButtonUseCurrBoard, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.ButtonNewFileUpload = wx.Button( self.PanelNewFileUpload, wx.ID_ANY, u"Select File", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.ButtonNewFileUpload, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )


		self.PanelNewFileUpload.SetSizer( bSizer9 )
		self.PanelNewFileUpload.Layout()
		bSizer9.Fit( self.PanelNewFileUpload )
		sbSizerNewFile.Add( self.PanelNewFileUpload, 1, wx.EXPAND |wx.ALL, 5 )


		bSizer4.Add( sbSizerNewFile, 0, wx.EXPAND, 5 )

		self.PanelOperations = wx.Panel( self.PanelFeatures, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer15 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer13 = wx.BoxSizer( wx.VERTICAL )

		sbSizerAlignBoards = wx.StaticBoxSizer( wx.StaticBox( self.PanelOperations, wx.ID_ANY, u"Align Boards" ), wx.VERTICAL )

		self.PanelAlignBoards1 = wx.ScrolledWindow( sbSizerAlignBoards.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.PanelAlignBoards1.SetScrollRate( 5, 5 )
		self.PanelAlignBoards1.Hide()

		sbSizerAlignBoards.Add( self.PanelAlignBoards1, 1, wx.EXPAND |wx.ALL, 5 )

		self.PanelAlignBoards = wx.Panel( sbSizerAlignBoards.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sbSizerAlignBoards.Add( self.PanelAlignBoards, 1, wx.EXPAND |wx.ALL, 5 )


		bSizer13.Add( sbSizerAlignBoards, 1, wx.EXPAND|wx.LEFT, 0 )

		sbSizerCompLayers = wx.StaticBoxSizer( wx.StaticBox( self.PanelOperations, wx.ID_ANY, u"Layers to Compare" ), wx.VERTICAL )

		self.PanelCompLayers = wx.Panel( sbSizerCompLayers.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.PanelCompLayers.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

		bSizer2 = wx.BoxSizer( wx.VERTICAL )

		listBoxCompLayersChoices = []
		self.listBoxCompLayers = wx.ListBox( self.PanelCompLayers, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, listBoxCompLayersChoices, wx.LB_MULTIPLE )
		bSizer2.Add( self.listBoxCompLayers, 1, wx.ALL|wx.EXPAND, 5 )

		bSizer16 = wx.BoxSizer( wx.VERTICAL )

		rbCompMethodChoices = [ u"Component", u"Line", u"Hybrid" ]
		self.rbCompMethod = wx.RadioBox( self.PanelCompLayers, wx.ID_ANY, u"Comparison Method", wx.DefaultPosition, wx.DefaultSize, rbCompMethodChoices, 1, wx.RA_SPECIFY_COLS )
		self.rbCompMethod.SetSelection( 0 )
		bSizer16.Add( self.rbCompMethod, 0, wx.ALL, 5 )

		self.cbExportOriginal = wx.CheckBox( self.PanelCompLayers, wx.ID_ANY, u"Export Original Board", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer16.Add( self.cbExportOriginal, 0, wx.ALL, 5 )


		bSizer2.Add( bSizer16, 2, wx.ALIGN_RIGHT, 5 )


		self.PanelCompLayers.SetSizer( bSizer2 )
		self.PanelCompLayers.Layout()
		bSizer2.Fit( self.PanelCompLayers )
		sbSizerCompLayers.Add( self.PanelCompLayers, 1, wx.EXPAND|wx.ALL, 5 )


		bSizer13.Add( sbSizerCompLayers, 0, wx.EXPAND, 5 )


		bSizer15.Add( bSizer13, 1, wx.EXPAND, 0 )


		self.PanelOperations.SetSizer( bSizer15 )
		self.PanelOperations.Layout()
		bSizer15.Fit( self.PanelOperations )
		bSizer4.Add( self.PanelOperations, 1, wx.EXPAND |wx.ALL, 0 )


		bSizer22.Add( bSizer4, 1, wx.EXPAND, 5 )


		self.PanelFeatures.SetSizer( bSizer22 )
		self.PanelFeatures.Layout()
		bSizer22.Fit( self.PanelFeatures )
		bSizer14.Add( self.PanelFeatures, 1, wx.EXPAND |wx.ALL, 5 )

		self.PanelLog = wx.ScrolledWindow( self.PanelAll, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.PanelLog.SetScrollRate( 5, 5 )
		self.PanelLog.SetMinSize( wx.Size( 75,75 ) )

		bSizer14.Add( self.PanelLog, 0, wx.ALL|wx.EXPAND, 5 )

		bSizer21 = wx.BoxSizer( wx.HORIZONTAL )

		self.ButtonEditParams = wx.Button( self.PanelAll, wx.ID_ANY, u"Edit Analysis Params", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer21.Add( self.ButtonEditParams, 0, wx.ALL, 5 )

		self.ButtonCompare = wx.Button( self.PanelAll, wx.ID_ANY, u"Compare and Export", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer21.Add( self.ButtonCompare, 0, wx.ALL, 5 )

		self.ButtonOK = wx.Button( self.PanelAll, wx.ID_ANY, u"Exit and Open in Kicad", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer21.Add( self.ButtonOK, 0, wx.ALL, 5 )


		bSizer14.Add( bSizer21, 0, wx.ALIGN_RIGHT, 5 )


		self.PanelAll.SetSizer( bSizer14 )
		self.PanelAll.Layout()
		bSizer14.Fit( self.PanelAll )
		bSizer6.Add( self.PanelAll, 1, wx.EXPAND |wx.ALL, 10 )


		self.SetSizer( bSizer6 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.OnClose )
		self.ButtonOldFileUpload.Bind( wx.EVT_BUTTON, self.UploadOldFile )
		self.ButtonUseCurrBoard.Bind( wx.EVT_BUTTON, self.UseCurrentBoard )
		self.ButtonNewFileUpload.Bind( wx.EVT_BUTTON, self.UploadNewFile )
		self.rbCompMethod.Bind( wx.EVT_RADIOBOX, self.ComparisonMethodChanged )
		self.ButtonEditParams.Bind( wx.EVT_BUTTON, self.EditParams )
		self.ButtonCompare.Bind( wx.EVT_BUTTON, self.CompareBoards )
		self.ButtonOK.Bind( wx.EVT_BUTTON, self.OKClicked )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def OnClose( self, event ):
		event.Skip()

	def UploadOldFile( self, event ):
		event.Skip()

	def UseCurrentBoard( self, event ):
		event.Skip()

	def UploadNewFile( self, event ):
		event.Skip()

	def ComparisonMethodChanged( self, event ):
		event.Skip()

	def EditParams( self, event ):
		event.Skip()

	def CompareBoards( self, event ):
		event.Skip()

	def OKClicked( self, event ):
		event.Skip()


