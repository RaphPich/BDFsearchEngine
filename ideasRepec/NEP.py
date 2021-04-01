#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup 

PATH = "ideasRepec/"
FILE_NAME_NEP = "NEP.txt"

BASE_URL = 'https://ideas.repec.org/'
NEP_URL = 'https://ideas.repec.org/i/e.html'

#Retourne les codes NEP sous forme de 2 listes, 
#	- nep[0] la description du code NEP
#	- nep[1] l'url du code nep
def load_nep():
	data = [[],[]]
	with open(PATH+FILE_NAME_NEP) as file:
		for line in file:
			data[0].append(line.rstrip().rsplit('|')[0])
			data[1].append(line.rstrip().rsplit('|')[1])

	sort_list = [elem[4:] for elem in data[0] if elem!="ARA MENA - Middle East & North Africa"]
	sort_list+=["Middle East & North Africa"]

	data_sorted = [x for _,x in sorted(zip(sort_list,data[1]))]
	sort_list = [x for x,_ in sorted(zip(sort_list,data[1]))]
	return [sort_list,data_sorted]

#Retourne la liste des économistes
#	- data[0] liste de nom d'économistes
#	- data[1] liste d'url
def economists_nep(nep_code):
	indexe = nep[0].index(nep_code[0])
	url = nep[1][indexe]
	data = [[],[]]
	html_doc =requests.get(BASE_URL+url)
	soup = BeautifulSoup(html_doc.text,'html.parser')
	soup = soup.find("div",{"id":"content-block"})

	for elem1 in soup.find_all('table'):
		for elem2 in elem1.find_all("a",href = True):
			data[0].append(elem2.text)
			data[1].append(BASE_URL[:-1]+elem2["href"])
	return data

nep = load_nep()