import sys
sys.path.append("/usr/local/lib/python2.7/site-packages")
from PyQt4 import QtGui, QtCore
from ankiquest import *

class Example(QtGui.QWidget):

	def __init__(self):
		super(Example, self).__init__()
		self.initUI()

	def initUI(self):	 
		self.AQState = AnkiQuester()
		self.AQUI = UserInterface(self.AQState)
		self.font = QtGui.QFont("Inconsolata", 12)
		self.font.setLetterSpacing(1, 2)
		self.fontoptions = QtGui.QTextOption()
		self.fontoptions.setAlignment(QtCore.Qt.AlignAbsolute)
		self.lineheight = QtGui.QFontMetrics(self.font).height()
		self.charwidth = QtGui.QFontMetrics(self.font).averageCharWidth() + self.font.letterSpacing()
		self.setGeometry(30, 30, self.charwidth*self.AQUI.ScreenWidth, self.lineheight*self.AQUI.ScreenHeight)
		self.setWindowTitle('AnkiQuest')
		self.setStyleSheet("background-color: black")
		self.show()
	
	def paintEvent(self, event):
		qp = QtGui.QPainter()
		qp.begin(self)
		qp.setFont(self.font)
		qp.setPen(QtGui.QColor("White"))
		self.text = self.AQUI.RenderScreen()
		qp.drawText(QtCore.QRectF(event.rect()), self.text, self.fontoptions)
		qp.end()
		
	
	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_F2:
			qt_trace()
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