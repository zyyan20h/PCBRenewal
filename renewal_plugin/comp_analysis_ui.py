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

		bSizer19 = wx.BoxSizer( wx.HORIZONTAL )

		self.ButtonSaveParams = wx.Button( self, wx.ID_ANY, u"Save Parameters to File", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.ButtonSaveParams, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.ButtonDefaultParams = wx.Button( self, wx.ID_ANY, u"Restore Defaults", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.ButtonDefaultParams, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.ButtonOK = wx.Button( self, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.ButtonOK, 0, wx.ALL, 5 )


		bSizer16.Add( bSizer19, 0, wx.ALIGN_RIGHT, 5 )


		self.SetSizer( bSizer16 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.OnClose )
		self.ButtonSaveParams.Bind( wx.EVT_BUTTON, self.SaveParameters )
		self.ButtonDefaultParams.Bind( wx.EVT_BUTTON, self.RestoreDefaults )
		self.ButtonOK.Bind( wx.EVT_BUTTON, self.OKClicked )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def OnClose( self, event ):
		event.Skip()

	def SaveParameters( self, event ):
		event.Skip()

	def RestoreDefaults( self, event ):
		event.Skip()

	def OKClicked( self, event ):
		event.Skip()


