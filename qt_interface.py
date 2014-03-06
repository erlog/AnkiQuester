from ankiquest import *

try:
	from aqt.qt import *
	from aqt import mw
	AQ_DEBUG = False
	
except ImportError:
	AQ_DEBUG = True
	import sys
	sys.path.append("/usr/local/lib/python2.7/site-packages")
	from PyQt4.QtGui import *
	from PyQt4.QtCore import *
	
#If we're in Anki then we add the AQ menu item and clone _answerCard for later
if not AQ_DEBUG:
	def AQ_Start():
		mw.AQ_AnkiWindow = AQ_Anki_Window = AQ_QT_Interface()
		AQ_Anki_Window.show()
	
	def catch_answer(ease):
		OLD_answerCard(ease)

	action = QAction("AnkiQuest", mw)
	mw.connect(action, SIGNAL("triggered()"), AQ_Start)
	mw.form.menuTools.addAction(action)
	
	OLD_answerCard = mw.reviewer._answerCard

class AQ_QT_Interface(QDialog):
	def __init__(self):
		super(AQ_QT_Interface, self).__init__()
		self.initUI()

	def initUI(self):	 
		self.AQState = AnkiQuester()
		self.AQUI = UserInterface(self.AQState)
		self.font = QFont("Inconsolata", 12)
		self.font.setLetterSpacing(1, 2)
		self.fontoptions = QTextOption()
		self.font.setStyleHint(QFont.TypeWriter)
		self.fontoptions.setAlignment(Qt.AlignAbsolute)
		self.lineheight = QFontMetrics(self.font).height()
		self.charwidth = QFontMetrics(self.font).averageCharWidth() + self.font.letterSpacing()
		self.setGeometry(30, 30, self.charwidth*self.AQUI.ScreenWidth, self.lineheight*self.AQUI.ScreenHeight)
		self.setWindowTitle('AnkiQuest')
		self.setStyleSheet("background-color: black")
		self.show()
	
	def paintEvent(self, event):
		qp = QPainter()
		qp.begin(self)
		qp.setFont(self.font)
		qp.setPen(QColor("White"))
		self.text = self.AQUI.RenderScreen()
		qp.drawText(QRectF(event.rect()), self.text, self.fontoptions)
		qp.end()
		
	def keyPressEvent(self, event):
		if event.key() == Qt.Key_F2:
			qt_trace()
		elif event.key() == Qt.Key_Up: self.AQState.PlayerMove("Up")
		elif event.key() == Qt.Key_Down: self.AQState.PlayerMove("Down")
		elif event.key() == Qt.Key_Left: self.AQState.PlayerMove("Left")
		elif event.key() == Qt.Key_Right: self.AQState.PlayerMove("Right")
		elif event.key() == Qt.Key_Space: self.AQState.PlayerMove("Rest")
		elif event.key() == Qt.Key_Escape: self.close()
		self.update()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = AQ_QT_Interface()
	sys.exit(app.exec_())

	
	
