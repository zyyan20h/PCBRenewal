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
## Class SelectionWindow
###########################################################################

class SelectionWindow ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 330,159 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer10 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Select an Edge", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
		self.m_staticText4.Wrap( -1 )

		bSizer10.Add( self.m_staticText4, 2, wx.ALL|wx.EXPAND, 5 )


		bSizer10.Add( ( 0, 0), 1, 0, 5 )

		bSizer11 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer11.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.ButtonSelectionCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer11.Add( self.ButtonSelectionCancel, 0, wx.ALL, 5 )


		bSizer11.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.ButtonSelectionDone = wx.Button( self, wx.ID_ANY, u"Done", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer11.Add( self.ButtonSelectionDone, 0, wx.ALL, 5 )


		bSizer11.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		bSizer10.Add( bSizer11, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer10 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.DialogClosed )
		self.ButtonSelectionCancel.Bind( wx.EVT_BUTTON, self.CancelSelection )
		self.ButtonSelectionDone.Bind( wx.EVT_BUTTON, self.ComponentSelected )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def DialogClosed( self, event ):
		event.Skip()

	def CancelSelection( self, event ):
		event.Skip()

	def ComponentSelected( self, event ):
		event.Skip()


