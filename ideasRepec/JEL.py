import requests
from bs4 import BeautifulSoup 

URL_JEL_IDEAS = 'https://ideas.repec.org/j/'

def url_jel(jel_code):
	return URL_JEL_IDEAS+jel_code+'.html'

def articles_from_jel_url(url):
	html_doc =requests.get(url)
	soup = BeautifulSoup(html_doc.text,'html.parser')

	description,articles = [],[]

	for elem in soup.find_all('ul',{'class':'list-group paper-list'}):
		article = elem.find_all('b')
		for line in article:
			description.append(line.find('a').text)
			articles.append(line.find('a')['href'])
	return [description,articles]

def articles_from_jel(jel_code):
	return articles_from_jel(url_jel(jel_code))
	