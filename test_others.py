from subprocess import Popen, PIPE
from docx import opendocx, getdocumenttext


def document_to_text(filename, file_path):
	output = open('/home/yung/download/output_odt.txt','w')
	if filename[-4:] == ".doc":
		cmd = ['antiword', file_path]
		p = Popen(cmd, stdout = PIPE)
		stdout, stderr = p.communicate()
		temp_odt = stdout.decode('ascii','ignore')
		return temp_odt
	elif filename[-5:] == ".docx":
		document = opendocx(file_path)
		paratextlist = getdocumenttext(document)
		newparatextlist = []
		for paratext in paratextlist:
			temp_docx = paratext.encode("utf-8")
			newparatextlist.append(temp_docx)
			output.write(temp_docx)
		return '\n\n'.join(newparatextlist)
	elif filename[-4:] == ".odt":
		cmd = ['odt2txt',file_path]
		p = Popen(cmd, stdout = PIPE)
		stdout, stderr = p.communicate()
		temp_odt = stdout.decode('ascii','ignore')
		output.write(temp_odt)
		return temp_odt
	else:
		print "Can't convert"
	output.close()



if __name__ == '__main__':
	file_path = '/home/yung/download/Spelling_and_Grammar.odt'
	temp_name = file_path.split('/')
	filename = temp_name[len(temp_name)-1]
	print filename
	document_to_text(filename,file_path)