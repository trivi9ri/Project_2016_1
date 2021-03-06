import sys 
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
import sys
import os
import time
class MyListView(QListView):
	def ItemClicked(self,index):
		QMessageBox.information(None,"dk","ds")

class filedialogdemo(QWidget):
 	def __init__(self,parent = None):
		super(filedialogdemo, self).__init__(parent)


		layout = QVBoxLayout()
		layout.addStretch()
	
		self.le = QLabel("Select file and push Conversion button")

		layout.addWidget(self.le)
		self.btn1 = QPushButton("File open")
		self.btn1.clicked.connect(self.getfiles)
		layout.addWidget(self.btn1)

		
		self.setLayout(layout)
		self.setWindowTitle("Open file")

		self.btn2 = QPushButton("Conversion to text")
		self.btn2.clicked.connect(self.convert_pdf_to_txt)
		layout.addWidget(self.btn2)

		self.ql = QLineEdit()
		self.ql.setObjectName("Keyword")
		self.ql.setText("Input Keyword what you search")
		self.btn3 = QPushButton("Search")
		self.btn3.clicked.connect(self.search)
		layout.addWidget(self.ql)
		layout.addWidget(self.btn3)

		self.fl = MyListView(None)
		self.model = QStringListModel()

	def getfiles(self):
		dlg = QFileDialog()
		dlg.setFileMode(QFileDialog.AnyFile)
		dlg.setFilter("Pdf files (*.pdf)")
		filename = QStringList()

		if dlg.exec_():
			filenames = dlg.selectedFiles()
			global f
			f = filenames[0]
		

	def convert_pdf_to_txt(self):
		token = f.split('/')
		input_file = token[-1]
		filename_extension = input_file[-3:]
		outtxt = '/home/yung/Python_project/'+'txt_'+input_file[:-3]+'txt'
		# if (filename_extension == 'pdf'):

		
		
		rsrcmgr = PDFResourceManager()
		retstr = StringIO()
		codec = 'utf-8'
		laparams = LAParams()
		device = TextConverter(rsrcmgr, retstr, codec = codec, laparams = laparams)
		fp = file(f, 'rb')
		output = open(outtxt,'w')
		interpreter = PDFPageInterpreter(rsrcmgr, device)
		password = ""
		maxpages = 0
		caching = True
		pagenos = set()
		for page in PDFPage.get_pages(fp, pagenos, maxpages = maxpages, password = password, caching = caching, check_extractable = True):
			interpreter.process_page(page)
		fp.close()
		device.close()
		strg= retstr.getvalue()
		output.write(strg)
		retstr.close()
		output.close()
		os_input = 'python modified_topic_modelig_and_frequency.py '+outtxt
		os.system(str(os_input))
		return strg	


	def search(self):
	 	search_keyword = str(self.ql.text()).lower()
	 	result = []
	 	file_string = ''
	 	search_list = []
	 	start_time = time.time()
	 	with open("TOPIC10_TOP15.csv") as archive:
    			archive.readline()
    			for line in archive:
    				if (search_keyword in line.lower()):
    					result.append(line)
    					
    			if (len(result)  == 0):
    				print "No such File!"
    			else:
    				for a in result:
    					token2 = a.split(',')
    					search_file =  token2[-1]
    					search_list.append(search_file[:-1])
    				  
    				search_list = list(set(search_list))
    				
    				file_string = ''
    				for b in range(len(search_list)):
    					file_string = file_string + search_list[b] + ';'

    				print file_string
    				print search_list
    				print len(search_list)
    				self.model.setStringList(QString(file_string).split(";"))
    				self.fl.setModel(self.model)
    				self.fl.setWindowTitle("File list")
    				self.fl.show()

    				# QObject.connect(self.fl, SIGNAL("clicked(QModelIndex)"),
    				# 	self.fl,SLOT("ItemClicked(QModelIndex)"))
    			end_time = time.time()
    			print end_time - start_time
    			print "Search is successfuly finish!"
       


def main():
	app = QApplication(sys.argv)
	ex = filedialogdemo()
	ex.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
	