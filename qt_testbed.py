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
		self.ScreenHeight = 50
		self.StatusWidth = 15
		self.StatusHeight = self.ScreenHeight
		self.MsgWidth = self.ScreenWidth-self.StatusWidth
		self.MsgHeight = 6
		self.DungeonWidth = self.ScreenWidth - self.StatusWidth
		self.DungeonHeight = self.ScreenHeight - self.MsgHeight
		
		self.AQState = AnkiQuester()
		self.font = QtGui.QFont("Inconsolata", 12)
		self.fontoptions = QtGui.QTextOption()
		self.fontoptions.setAlignment(QtCore.Qt.AlignAbsolute)
		self.setGeometry(20, 20, 550, 550)
		self.setWindowTitle('AnkiQuest')
		self.show()
	
	def paintEvent(self, event):
		qp = QtGui.QPainter()
		qp.begin(self)
		qp.setFont(self.font)
		self.drawText(event, qp)
		qp.end()

	def drawText(self, event, qp):
		self.text = str(self.AQState.CurrentFloor)
		qp.drawText(QtCore.QRectF(event.rect()), self.text, self.fontoptions)	
	
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