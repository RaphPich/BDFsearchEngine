#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread
from ideasRepec.update import load_economist,URL_BASE_IDEAS
#Utilisation d'une queue pour y stocker les informations personnelles des économistes
q = Queue(maxsize=0)

#Retourne les url d'un ensemble d'économistes dont les noms et prénoms contiennent les éléments de name_list
def economist_url(name_list):
	data = load_economist()
	urls = []
	for name,url_add in zip(data[0],data[1]):
		if sum([elem in name for elem in name_list])==len(name_list):
			urls.append(URL_BASE_IDEAS+url_add)
	if not urls:
		return None
	return urls

#Retourne tous les articles et les liens à partir d'un url d'économiste
#	data_sorted[0]: Description de l'article
#	data_sorted[1]: Lien de l'article
#	data_sorted[2]: Date de l'article
def economist_articles(url = False,soup = False):
	if url:
		html_doc =requests.get(url)
		soup = BeautifulSoup(html_doc.text,'html.parser')
	data = [[],[],[]]
	#Articles et liens

	soup = soup.find('div',{'id':'research'})

	for elem in soup.find_all('li',{'class':'list-group-item downfree'}):
		data[2].append(elem.text.rsplit("\n")[0].rsplit(" ")[-1][:-1])
		data[0].append(elem.find('a').text)
		if 'https://' in elem.find('a')['href']:
			data[1].append(elem.find('a')['href'])
		else:
			data[1].append(URL_BASE_IDEAS+elem.find('a')['href'])

	data_sorted = [[],[],[]]
	for x,y,z in sorted(zip(data[2],data[0],data[1])):
			data_sorted[0].append(y)
			data_sorted[1].append(z)
			data_sorted[2].append(x)
	return data_sorted

#Met dans la queue le dictionnaire d'infos personnelles d'un économiste en scrapant à partir de son url ou soup
def economist_personal_informations(url = False,soup = False):
	if url:
		try:
			html_doc =requests.get(url)
		except requests.exceptions.ConnectionError:
			print("Connection refused")
			return
		soup = BeautifulSoup(html_doc.text,'html.parser')
	personal_informations = {}
	affiliation = economist_affiliations(soup = soup)

	if affiliation:
		personal_informations['Affiliations'] = " ".join(affiliation)
	else:
		personal_informations["Affiliations"] = "N/A"

	soup = soup.find('div',{"id":"person"})
	if soup==None:
		return None
	soup = soup.find("table")
	if soup==None:
		return None

	for elem in soup.find_all('tr'):
		line = elem.find_all('td')
		try:
			if line[0].text != None:
				personal_informations[line[0].text] = line[1].text
			if line[0].get('class') != None:
				personal_informations[line[0].get("class")[0]] = line[1].text
		except:
			pass
			
	q.put(personal_informations)

#Retourne la liste d'informations personnelles (sous forme de dict) d'économistes
def eco_perso_info_urls(urls):
	tab = []
	threads = []
	#Les requetes sont chronophages, d'où l'utilisation de thread 
	for url in urls:
		worker = Thread(target=economist_personal_informations, args=(url,))
		worker.setDaemon(True)
		threads.append(worker)
		worker.start()

	#On attend la fin des thread
	for elem in threads:
		elem.join()
	#Récupération des informations personnelles
	while not q.empty():
		tab.append(q.get())
	return tab

#Scrap et retourne les affiliations d'un économiste
def economist_affiliations(url = False,soup = False):
	if url:
		html_doc =requests.get(url)
		soup = BeautifulSoup(html_doc.text,'html.parser')

	soup = soup.find('div',{'id' : 'affiliation'})	

	if soup!=None:
		return [elem.text for elem in soup.find_all('h3')]

	return False


