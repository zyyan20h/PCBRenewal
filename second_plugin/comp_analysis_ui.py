# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.0.0-0-g0efcecf)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.grid

###########################################################################
## Class AnalysisDialog
###########################################################################

class AnalysisDialog ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 658,428 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer16 = wx.BoxSizer( wx.VERTICAL )

		bSizer17 = wx.BoxSizer( wx.HORIZONTAL )

		sbSizer5 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Parameters from config.ini" ), wx.VERTICAL )

		self.PanelConfigParams = wx.ScrolledWindow( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.PanelConfigParams.SetScrollRate( 5, 5 )
		sbSizer5.Add( self.PanelConfigParams, 1, wx.EXPAND |wx.ALL, 5 )


		bSizer17.Add( sbSizer5, 20, wx.EXPAND, 5 )

		sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"User Parameters" ), wx.VERTICAL )

		self.PanelUserParams = wx.ScrolledWindow( sbSizer6.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.PanelUserParams.SetScrollRate( 5, 5 )
		sbSizer6.Add( self.PanelUserParams, 1, wx.EXPAND |wx.ALL, 5 )


		bSizer17.Add( sbSizer6, 20, wx.EXPAND, 5 )


		bSizer16.Add( bSizer17, 1, wx.EXPAND, 5 )

		self.GridAnalysis = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

		# Grid
		self.GridAnalysis.CreateGrid( 3, 4 )
		self.GridAnalysis.EnableEditing( True )
		self.GridAnalysis.EnableGridLines( True )
		self.GridAnalysis.EnableDragGridSize( False )
		self.GridAnalysis.SetMargins( 0, 0 )

		# Columns
		self.GridAnalysis.EnableDragColMove( False )
		self.GridAnalysis.EnableDragColSize( True )
		self.GridAnalysis.SetColLabelValue( 0, u"Time" )
		self.GridAnalysis.SetColLabelValue( 1, u"Material" )
		self.GridAnalysis.SetColLabelValue( 2, u"Price" )
		self.GridAnalysis.SetColLabelValue( 3, u"Energy" )
		self.GridAnalysis.SetColLabelValue( 4, wx.EmptyString )
		self.GridAnalysis.SetColLabelValue( 5, wx.EmptyString )
		self.GridAnalysis.SetColLabelSize( wx.grid.GRID_AUTOSIZE )
		self.GridAnalysis.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

		# Rows
		self.GridAnalysis.AutoSizeRows()
		self.GridAnalysis.EnableDragRowSize( True )
		self.GridAnalysis.SetRowLabelValue( 0, u"Using Blank Board" )
		self.GridAnalysis.SetRowLabelValue( 1, u"Using Current Board" )
		self.GridAnalysis.SetRowLabelValue( 2, u"Resources Saved" )
		self.GridAnalysis.SetRowLabelValue( 3, wx.EmptyString )
		self.GridAnalysis.SetRowLabelValue( 4, wx.EmptyString )
		self.GridAnalysis.SetRowLabelValue( 5, wx.EmptyString )
		self.GridAnalysis.SetRowLabelSize( wx.grid.GRID_AUTOSIZE )
		self.GridAnalysis.SetRowLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

		# Label Appearance

		# Cell Defaults
		self.GridAnalysis.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		bSizer16.Add( self.GridAnalysis, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )


		self.SetSizer( bSizer16 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.OnClose )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def OnClose( self, event ):
		event.Skip()


