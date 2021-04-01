#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup 
import string
import sys
from ideasRepec.update import load_institutions,URL_BASE_EDIRC

#Charge les économistes de l'institution associée à l'url
def economist_from_institution_url(url):
	html_doc =requests.get(url)
	soup = BeautifulSoup(html_doc.text,'html.parser')
	soup = soup.find('div',{'id':'members'})
	if soup == None:
		return []
	urls = []
	for elem in soup.find_all('a',href = True):
		if 'html' in elem['href']:
			urls.append("https"+elem['href'][4:])

	return urls
	
#Recherche une institution dans le fichier institution.txt
#	institutions[0]: nom de l'institution
#	institutions[1]: url de l'institution
def search_institution(words):

	def words_in_descr(words,descr):
		for elem in words:
			if elem not in descr:
				return False
		return True

	[description,urls] = load_institutions()
	institutions = [[],[]]

	for a,b in zip(description,urls):
		if words_in_descr(words,a.rsplit(" ")):
			institutions[0].append(a)
			institutions[1].append(URL_BASE_EDIRC+b)
	if not institutions[0]:
		return False
	return institutions

#Charge les économistes associé aux mots clés de l'institution
def economists_from_institutions(institutions_name_search):

	institutions = search_institution(institutions_name_search)

	if not institutions:
		print("No institutions found")
		return False

	institutions_with_economists = [[],[]]
	economists_urls = []

	for name,url in zip(institutions[0],institutions[1]):
		liste = economist_from_institution_url(url)
		if len(liste)!=0:
			institutions_with_economists[0].append(name)
			institutions_with_economists[1].append(url)
			economists_urls+=liste

	return [institutions_with_economists,economists_urls]

	