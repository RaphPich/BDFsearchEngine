import requests
from bs4 import BeautifulSoup 

PATH = 'classification/'
FILE_NAME='JEL.txt'

def update_jel():
	url = "https://www.aeaweb.org/econlit/classificationTree.xml"

	html_doc =requests.get(url)

	soup = BeautifulSoup(html_doc.text,'html.parser')

	JEL = [[],[]]

	for classification in soup.find_all('classification'):
		code = classification.find('code').text
		description = classification.find('description').text

		JEL[0].append(code)
		JEL[1].append(description)


	with open("JEL.txt", 'w+') as file:
		for code,description in zip(JEL[0],JEL[1]):
			file.write("|".join([code,description])+"\n")

def load_jel():
	JEL = [[],[]]
	with open(PATH+FILE_NAME, 'r') as file:
		for line in file:
			code,description = line.rstrip().rsplit("|")
			JEL[0].append(code)
			JEL[1].append(description)
	return JEL

#Return list of code or keyword, if not find return False
def search_jel(code=False,key_word = False):

	def search_code(code,jel):
		for a,b in zip(jel[0],jel[1]):
			if a == code:
				return b
		return False

	JEL = load_jel()

	jel_returned = []

	if key_word:
		key_word = key_word.lower()

		for code,description in zip(JEL[0],JEL[1]):
			if key_word in description.lower():
				jel_returned.append([code,description])
		if not jel_returned:
			return False
		return jel_returned

	if code :
		if type(code) is list:
			for elem in code:
				jel_returned.append(search_code(elem,jel))
		elif type(code) is str:
			return search_code(code,jel)



	return False

jel = load_jel()