import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QPlainTextEdit, QFrame, QLabel, QFileDialog, QSpinBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSlot

import io

from omniaUI                import OmniaUI

class App(QMainWindow):

	def __init__(self):
		super(App, self).__init__()
		uic.loadUi('editor.ui', self)

		self.fileFullName=""

		# Create textbox
		self.textbox = self.findChild(QPlainTextEdit,"textbox")
		
		# Create a button in the window
		self.draw_btn = self.findChild(QPushButton,"draw")
		self.rotate_btn = self.findChild(QPushButton,"rotate")
		self.save_btn = self.findChild(QPushButton,"save")
		self.save_as_btn = self.findChild(QPushButton,"save_as")
		self.open_btn = self.findChild(QPushButton,"open")
		self.resize_btn = self.findChild(QPushButton,"resize")
		self.quit_btn = self.findChild(QPushButton,"quit")


		# Create a spin box in the window
		self.height_box= self.findChild(QSpinBox,"height")
		self.width_box= self.findChild(QSpinBox,"width")

		# Create filename label
		self.file_label = self.findChild(QLabel,"file_label")
		# Create image
		ui_width = self.width_box.value()
		ui_height = self.height_box.value()

		self.img_label = self.findChild(QLabel,"img_label")
		
		self.img_label.setFrameShape(QFrame.Panel)        

		self.omniaui = OmniaUI((ui_width, ui_height))

		self.image = QPixmap()

		self.drawImg()

		self.img_label.setPixmap(self.image)

		# connect button to function on_click
		self.draw_btn.clicked.connect(self.draw_ui)
		self.rotate_btn.clicked.connect(self.rotate_ui)
		self.save_btn.clicked.connect(self.save_ui)
		self.save_as_btn.clicked.connect(self.save_as_ui)
		self.open_btn.clicked.connect(self.open_ui)
		self.resize_btn.clicked.connect(self.resize_ui)
		self.quit_btn.clicked.connect(self.quit_ui)

		self.showFullScreen()      
	
	def drawImg(self, xml_string=''):
		if xml_string != '':
			self.omniaui.loadFromXML(xml_string)
		
		img = self.omniaui.get_image()
		w,h = img.size
		#print(w,h)
		
		f = io.BytesIO()
		img.save(f, "png")
		buf = f.getbuffer()
		self.image.loadFromData(buf)
		del buf
		f.close()

		self.img_label.setPixmap(self.image)

	@pyqtSlot()
	def rotate_ui(self):
		self.omniaui.changeOrientation()

		orientation = self.omniaui.getOrientation()
		width=self.width_box.value()
		height=self.height_box.value()
		self.height_box.setValue(width)
		self.width_box.setValue(height)

		self.drawImg()

		text = self.textbox.toPlainText()

		or_index = text.find("orientation=")

		if or_index == -1:
			#print(text.find("ui"))
			start = text.find("<ui") + 3
			end = text.find(">", start)
			ui_attrib = text[ start : end ].strip()
			ui_attrib += " orientation='"+orientation+"'"

			text = text[:start] +" "+ ui_attrib + text[end:]
			
		else:
			start = or_index + 13   # skip "orientation='"
			end = text.find("'",start)
			text = text[:start] + orientation + text[end:]
		
		self.textbox.setPlainText(text)     

	@pyqtSlot()
	def draw_ui(self):
		textboxValue = self.textbox.toPlainText()
		self.drawImg(textboxValue)
	
	@pyqtSlot()
	def save_as_ui(self):
		text = self.textbox.toPlainText()
		name = QFileDialog.getSaveFileName(self, "Save File", '.', '.xml')[0]
		if name != '':
			self.fileFullName=name + ".xml"
			self.file_label.setText(self.fileFullName)
	
			with open(name + ".xml", "w") as f:
				#_ = f.read()
				f.seek(0,0)
				f.write(text)
	
	@pyqtSlot()
	def save_ui(self):
		text = self.textbox.toPlainText()
		if self.fileFullName != '':
			self.file_label.setText(self.fileFullName)
			with open(self.fileFullName , "w") as f:
				#_ = f.read()
				f.seek(0,0)
				f.write(text)

	@pyqtSlot()
	def open_ui(self):
		name, _ = QFileDialog.getOpenFileName(self,"Open UI file", ".","XML files (*.xml)")
		
		if name != '':
			self.fileFullName=name
			self.file_label.setText(self.fileFullName)
			with open(self.fileFullName, "r") as f:
				content = f.read()
				self.textbox.setPlainText(content)
				self.drawImg(content)

	@pyqtSlot()
	def resize_ui(self):
		self.omniaui.height=self.height_box.value()
		self.omniaui.width=self.width_box.value()
		
		#necessary to redraw the image frame on the UI
		self.omniaui.changeOrientation()
		self.omniaui.changeOrientation()

		self.drawImg()

	@pyqtSlot()
	def quit_ui(self):
		sys.exit(0)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())