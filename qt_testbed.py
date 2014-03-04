import sys
sys.path.append("/usr/local/lib/python2.7/site-packages")
from PyQt4 import QtGui, QtCore
from time import time
from ankiquest import *
import pdb

class Example(QtGui.QWidget):

	def __init__(self):
		super(Example, self).__init__()

		self.initUI()

	def initUI(self):	 
		self.ScreenWidth = 80
		self.ScreenHeight = 40
		self.StatusWidth = 15
		self.StatusHeight = self.ScreenHeight
		self.MsgWidth = self.ScreenWidth - self.StatusWidth
		self.MsgHeight = 6
		self.DungeonWidth = self.ScreenWidth - self.StatusWidth
		self.DungeonHeight = self.ScreenHeight - self.MsgHeight
		
		self.AQState = AnkiQuester()
		self.font = QtGui.QFont("Inconsolata", 12)
		self.font.setStyleHint(QtGui.QFont.TypeWriter)
		self.font.setLetterSpacing(1, 2)
		self.fontoptions = QtGui.QTextOption()
		self.fontoptions.setAlignment(QtCore.Qt.AlignAbsolute)
		self.lineheight = QtGui.QFontMetrics(self.font).height()
		self.charwidth = QtGui.QFontMetrics(self.font).averageCharWidth() + self.font.letterSpacing()
		self.setGeometry(30, 30, (self.ScreenWidth)*self.charwidth, (self.ScreenHeight)*self.lineheight)
		self.setWindowTitle('AnkiQuest')
		self.setStyleSheet("background-color: black")
		self.show()
	
	def paintEvent(self, event):
		qp = QtGui.QPainter()
		qp.begin(self)
		qp.setFont(self.font)
		qp.setPen(QtGui.QColor("White"))
		self.drawText(event, qp)
		qp.end()

	def drawText(self, event, qp):
		top = self.AQState.PlayerY-(self.DungeonHeight/2)
		bottom = self.AQState.PlayerY+(self.DungeonHeight/2)
		left = self.AQState.PlayerX-(self.DungeonWidth/2)
		right = self.AQState.PlayerX+(self.DungeonWidth/2)
		self.text = self.AQState.CurrentFloor.RenderFloor(top, bottom, left, right)
		qp.drawText(QtCore.QRectF(event.rect()), self.text, self.fontoptions)
		qp.drawText(QtCore.QRectF(2, self.DungeonHeight*self.lineheight, self.ScreenWidth*self.charwidth, self.MsgHeight*self.lineheight), self.AQState.MessageWindow(self.MsgHeight), self.fontoptions)	
		qp.drawText(QtCore.QRectF((self.DungeonWidth-1)*self.charwidth, 0, self.StatusWidth*self.charwidth, self.ScreenHeight*self.lineheight), self.AQState.StatusWindow(), self.fontoptions)
	
	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_F2:
			QtCore.pyqtRemoveInputHook()
			pdb.set_trace()
		elif event.key() == QtCore.Qt.Key_Up: self.AQState.PlayerMove("Up")
		elif event.key() == QtCore.Qt.Key_Down: self.AQState.PlayerMove("Down")
		elif event.key() == QtCore.Qt.Key_Left: self.AQState.PlayerMove("Left")
		elif event.key() == QtCore.Qt.Key_Right: self.AQState.PlayerMove("Right")
		elif event.key() == QtCore.Qt.Key_Space: self.AQState.PlayerMove("Rest")
		elif event.key() == QtCore.Qt.Key_Escape: self.close()
		self.update()


if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	ex = Example()
	sys.exit(app.exec_())