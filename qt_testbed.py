import sys
sys.path.append("/usr/local/lib/python2.7/site-packages")
from PyQt4 import QtGui, QtCore
from ankiquest import *
import pdb

class Example(QtGui.QWidget):

	def __init__(self):
		super(Example, self).__init__()

		self.initUI()

	def initUI(self):	 
		self.setGeometry(0, 0, 500, 500)
		self.setWindowTitle('AnkiQuest')
		self.show()
		self.frames = 0

	def paintEvent(self, event):
		qp = QtGui.QPainter()
		qp.begin(self)
		self.drawText(event, qp)
		qp.end()

	def drawText(self, event, qp):
		self.floor = DungeonFloor().Map
		self.text = ""
		for row in self.floor:
			for cell in row:
				self.text += cell.Glyph
			self.text += "\n"
		qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)	


if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	ex = Example()
	sys.exit(app.exec_())