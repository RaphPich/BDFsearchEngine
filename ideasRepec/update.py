#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup 
from queue import Queue
from threading import Thread

PATH = "ideasRepec/"

FILE_NAME_ECONOMIST = 'economist.txt'
FILE_NAME_CATEGORIES = 'institution_categories.txt'
FILE_NAME_INSTITUTION = 'institution.txt'
FILE_NAME_NEP = "NEP.txt"
 
URL_BASE_EDIRC = 'https://edirc.repec.org/'
URL_BASE_IDEAS = "https://ideas.repec.org/"
URL_NEP = 'https://ideas.repec.org/i/e.html'
URL_CATERGORIE = 'https://edirc.repec.org/areas.html'

#Scrap tous les nep et écrit directement dans le fichier concerné
def update_nep():
	html_doc =requests.get(URL_NEP)
	soup = BeautifulSoup(html_doc.text,'html.parser')

	soup = soup.find('div',{"id" : 'author-field'})
	with open(PATH+FILE_NAME_NEP,'w+') as file:
		for elem in soup.find_all('li'):
			if '/i/' in elem.find('a')["href"]:
				file.write("|".join([elem.text[4:],elem.find('a')["href"]])+"\n")

#Scrap tous les économistes par ordre alphabétique et écrit directement dans le fichier concerné
#	L'update de tous les économistes est longue, d'où l'utilisation d'une liste de Thread pour
#	le chargement dans l'ordre alphabétique
def update_economist():
	from string import ascii_lowercase as alphabet
	q = Queue(maxsize = len(alphabet))
	data= [[],[]]
	threads = []

	def get_all_name_by_letter(letter):

		url_name_letters = "https://ideas.repec.org/i/e{}.html".format(letter)
		html_doc =requests.get(url_name_letters)
		soup = BeautifulSoup(html_doc.text,'html.parser')
		soup = soup.find('table')

		data_page = [[],[]]
		for elem in soup.find_all('a',href= True):
			data_page[0].append(elem.text)
			data_page[1].append(elem['href'])

		q.put(data_page)

	for letter in alphabet:

		worker = Thread(target=get_all_name_by_letter, args=(letter,))
		worker.setDaemon(True)
		threads.append(worker)
		worker.start()

	for elem in threads:
		elem.join()

	while not q.empty():
		df = q.get()
		data[0]+= df[0]
		data[1]+= df[1]

	data[0],data[1] = zip(*sorted(zip(data[0], data[1])))

	with open(PATH+FILE_NAME_ECONOMIST,'w+') as file:
		for name,url in zip(data[0],data[1]):
			file.write("|".join([name.replace(" ",""),url])+"\n")

#Scrap les catégories pour les institutions, écrit les données dans le fichier concerné
def update_categories():

	html_doc =requests.get(URL_CATERGORIE)
	soup = BeautifulSoup(html_doc.text,'html.parser')
	soup = soup.find('dl')

	description = []
	link = []
	for elem in soup.find_all('a'):
		link.append(URL_BASE_EDIRC+elem['href'])
		description.append(elem.text)

	with open(PATH+FILE_NAME_CATEGORIES,'w+') as file:
		for a,b in zip(description,link):
			file.write(a+"|"+b+"\n")

#Met à jours toutes les institutions et écrit dans institution.txt
def update_all_institution(categories_urls):

	all_institutions,all_urls = [],[]

	no_dupl = []

	for url in categories_urls:
		institution,urls = load_institution_from_categorie_url(url)
		all_institutions+= institution
		all_urls += urls

	for a,b in zip(all_institutions,all_urls):
		no_dupl.append("|".join([a,b])+"\n")
	no_dupl = dict.fromkeys(no_dupl)

	with open(PATH+FILE_NAME_INSTITUTION,'w+') as file:
		for elem in no_dupl:
			file.write(elem)

#Charge les institutions avec uniquement des économistes 
def load_institution_from_categorie_url(url):

	institution = []
	urls = []

	html_doc =requests.get(url)
	soup = BeautifulSoup(html_doc.text,'html.parser')

	replace_tab = ["(",")",",",",",'"']

	for elem in soup.find_all('li'):
		line = elem.find('a',href = True)
		#Verification qu'il y a des économistesavec la class et le style
		if "data" in line['href'] and elem.find('i',{'class' : 'fa fa-user','style':'color:blue'}) != None:
			texte = line.text.replace("\n"," ") + elem.text.replace("\n"," ")
			for rep in replace_tab:
				texte = texte.replace(rep," ")
			texte = list(dict.fromkeys(texte.lower().rsplit(" ")))
			institution.append(" ".join(texte))
			urls.append(line['href'])

	return institution,urls

#Charge les catégories
#	description : description des catégories
#	urls 		: les urls des catégories
def load_categories():
	description,urls = [],[]	
	with open(PATH+FILE_NAME_CATEGORIES,'r') as file:
		for line in file:
			description.append(line.rstrip().split('|')[0])
			urls.append(line.rstrip().split('|')[1])
	return [description,urls]

#Charge les institutions et les urls
#	description : description des institutions
#	urls 		: les urls des institutions
def load_institutions():

	descriptions,urls = [],[]

	with open(PATH+FILE_NAME_INSTITUTION,'r') as file:
		for line in file:
			[description,url] = line.rstrip().rsplit("|")
			descriptions.append(description)
			urls.append(url)

	return [descriptions,urls]

#Charge tous les économistes
#	data[0] : nom des économistes
#	data[1]	: les urls des institutions
def load_economist():
	data = [[],[]]
	with open(PATH+FILE_NAME_ECONOMIST, 'r') as file:
		for line in file:
			name,url = line.rstrip().rsplit("|")
			data[0].append(name.lower())
			data[1].append(url)
	return data

#Update tous les fichiers
def update_all():
	update_categories()
	categories = load_categories()
	update_all_institution(categories[1])
	update_nep()
	update_economist()