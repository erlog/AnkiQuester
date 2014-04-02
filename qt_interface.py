import ankiquest

#We need to check if we're running in Anki so we can import the right libraries.
#Any instance outside of Anki is considered Debug at the moment, but could change in the future.
#To-do: separate Anki-less from Debug
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
	
#If we're in Anki then we add the AQ menu item.
if not AQ_DEBUG:
	def AQ_Start():
		mw.AQ_AnkiWindow = AQ_Anki_Window = AQ_QT_Interface()
		AQ_Anki_Window.show()
		
	def catch_answer(ease):
		mw.AQ_AnkiWindow.AQState.ReceiveFlashcardAnswer(ease)
		mw.AQ_AnkiWindow.activateWindow()
		OLD_answerCard(ease)

	OLD_answerCard = mw.reviewer._answerCard
	
	action = QAction("AnkiQuest", mw)
	mw.connect(action, SIGNAL("triggered()"), AQ_Start)
	mw.form.menuTools.addAction(action)

else:
	import pdb
	mw = None
	def qt_trace(self):
		pyqtRemoveInputHook()
		pdb.set_trace()

class AQ_QT_Interface(QDialog):
	def __init__(self):
		super(AQ_QT_Interface, self).__init__()

		#hook _answerCard with our version
		if not AQ_DEBUG:
			mw.reviewer._answerCard = catch_answer
		
		self.initUI()

	def initUI(self):	 
		self.AQState = ankiquest.AnkiQuester(mw, AQ_DEBUG)
		self.AQUI = ankiquest.ConsoleUserInterface(self.AQState)
		
		self.font = QFont("Inconsolata", 12)
		self.font.setLetterSpacing(1, 2)
		self.fontoptions = QTextOption()
		self.font.setStyleHint(QFont.TypeWriter)
		self.fontoptions.setAlignment(Qt.AlignAbsolute)
		self.setWindowTitle('AnkiQuest')
		self.setStyleSheet("background-color: black")
		
		#This is a kludge right now until I bother to learn more about Qt
		#To-do: Cut the unreliable lineheight/charwidth metrics out of the equation by using a proper Qt widget implementation
		self.lineheight = QFontMetrics(self.font).height()
		self.charwidth = QFontMetrics(self.font).averageCharWidth() + self.font.letterSpacing()
		self.setGeometry(30, 30, self.charwidth*self.AQUI.ScreenWidth, self.lineheight*self.AQUI.ScreenHeight+5)
		
		self.show()
		pyqtRemoveInputHook()
	
	def paintEvent(self, event):
		qp = QPainter()
		qp.begin(self)
		qp.setFont(self.font)
		qp.setPen(QColor("White"))
		self.text = self.AQUI.RenderScreen()
		qp.drawText(QRectF(self.rect()), self.text, self.fontoptions)
		qp.end()
		
	def keyPressEvent(self, event):
		#We should be doing passthrough to our ConsoleUserInterface if we're going to lean on it this heavily
		#To-do: Remove this Qt input crutch and write a proper console input controller or a real Qt interface
		if event.key() == Qt.Key_F2:
			if AQ_DEBUG: qt_trace(self.AQUI)
		elif (event.key() == Qt.Key_Up) or (event.key() == Qt.Key_K): self.AQState.PlayerMove("Up")
		elif (event.key() == Qt.Key_Down) or (event.key() == Qt.Key_J): self.AQState.PlayerMove("Down")
		elif (event.key() == Qt.Key_Left) or (event.key() == Qt.Key_H): self.AQState.PlayerMove("Left")
		elif (event.key() == Qt.Key_Right) or (event.key() == Qt.Key_L): self.AQState.PlayerMove("Right")
		elif event.key() == Qt.Key_Y: self.AQState.PlayerMove("UpLeft")
		elif event.key() == Qt.Key_U: self.AQState.PlayerMove("UpRight")
		elif event.key() == Qt.Key_B: self.AQState.PlayerMove("DownLeft")
		elif event.key() == Qt.Key_N: self.AQState.PlayerMove("DownRight")
		elif event.key() == Qt.Key_Space: self.AQState.PlayerMove("Rest")
		elif event.key() == Qt.Key_Period: self.AQState.PlayerMove("Rest")
		elif event.key() == Qt.Key_Escape: self.close()
		self.update()
	
	def closeEvent(self, event):
		#restore the old _answerCard method when AQ is closed
		if not AQ_DEBUG:
			mw.reviewer._answerCard = OLD_answerCard
	
	
		

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = AQ_QT_Interface()
	sys.exit(app.exec_())

	
	
