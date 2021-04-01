import tabula
from PyPDF2 import PdfFileReader
import os 
import sys

FILE_NAME = [elem for elem in os.listdir() if elem[-4:] == ".pdf"][0]

print(FILE_NAME)

def get_num_page():
	from PyPDF2 import PdfFileReader
	reader = PdfFileReader(FILE_NAME)
	return reader.getNumPages()

start = 5

num_pages = get_num_page()
data = []

print('num_pages =',num_pages)

tables = tabula.read_pdf(FILE_NAME, pages =str(start)+"-"+str(num_pages), multiple_tables = True)

data = []
issues = []

for table in tables:
	for line in table.values:
		if len(line) == 4:
			data.append([str(elem).replace("\r","") for elem in line])
		else :
			issues.append(list(line))


#Issue correction
a =[elem for elem in issues if len(elem)==3]
b =[elem for elem in issues if len(elem)==1]
c = [b1+a1 for a1,b1 in zip(a,b)]

data = data+c


with open('data.txt','w+') as file:
	for line in data:

		file.write("|".join([str(elem) for elem in line])+"\n")
