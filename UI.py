#!/usr/bin/env python3
############################################
#                                          #
#   Hackathon Banque de France 2020,       #
#   Programme proposé par Raphaël Pichon.  #
#   Contact : pichon.raphael@icloud.com    #
#                                          #
############################################

from tkinter import *
from tkinter.ttk import *
import ideasRepec as ir
import webbrowser
import sys
from time import time

class Application(Tk):
    def __init__(self):
        Tk.__init__(self)

        if "-update" in sys.argv:
            print("Updating...")
            ir.update_all()
            print("Updating done")

        #Taille de la fenêtre
        self.h = 720
        self.w = 1500

        #Texte entré dans la barre de recherche
        self.name_text = StringVar()
        self.skill_text = StringVar()
        self.competence = ""
        self.institution_text = StringVar()

        self.sorted = [None,None]#Indexe et reverse 

        #Barre de recherche
        Label( self, text="Votre recherche :").pack()
        Label( self, text="Nom").pack()
        Entry(self, textvariable=self.name_text).pack()
        Label( self, text="Institution").pack()
        Entry(self, textvariable=self.institution_text).pack()

        self.competenceTableau = Treeview(self, columns=('competence'))
        self.competenceTableau.bind("<Double-1>", self.clicCompetenceTab)
        self.competenceTableau.heading('competence',text='Compétence')
        self.competenceTableau['show'] = 'headings'
        self.competenceTableau.column('competence',width = int(self.w/4))
        self.competenceTableau.pack(padx = 10, pady = (0, 10),expand=1)
        self.competenceTableau.insert('', 'end', values=('None',))
        for elem in ir.nep[0]:
                self.competenceTableau.insert('', 'end', values=(elem,))
        self.text_competence = Label(self,text ="Aucune compétence")
        self.text_competence.pack()

        #Bouton 'recherche','quitter' et detection d'appuie sur la touche entrer
        self.bind('<Return>', self.press_enter)
        Button( self, text="Recherche", command=self.press_button_enter).pack()
        Button( self, text="Exporter la recherche", command=self.press_button_export).pack()
        Button( self, text="Quitter", command=self.press_button_exit).pack()

        #Texte d'affichage du nombre d'économistes trouvés
        self.text_presentation = Label(self,text ="")
        self.text_presentation.pack()
        self.columns_tag = ['nomfamille', 'prenom','pageprincipale','adresse','telephone','affiliations']
        self.columns_name = ['Nom de famille','Prénom','Page principale','Adresse','Téléphone','Affiliations']
        #Affichage d'économistes et d'articles dans les tableaux
        self.tableau = Treeview(self, columns=tuple(self.columns_tag),show = 'headings')

        for i, (tag, name) in enumerate(zip(self.columns_tag, self.columns_name)):
            self.tableau.heading(tag, text=name,command = lambda i_=i : self.sortTree(i_))

        larg_tab_eco = int(self.w/6*0.9)
        self.tableau.column('nomfamille',width = int(larg_tab_eco*0.75))
        self.tableau.column('prenom',width = int(larg_tab_eco*0.75))
        self.tableau.column('pageprincipale',width = int(larg_tab_eco))
        self.tableau.column('adresse',width = int(larg_tab_eco))
        self.tableau.column('telephone',width = int(larg_tab_eco*0.5))
        self.tableau.column('affiliations',width = int(larg_tab_eco*1.5))

        #Ajout de l'option d'appuyer 2 fois sur un économiste
        self.tableau.bind("<Double-1>", self.clicEconomistTab)
        self.tableau.pack(padx = 10, pady = (0, 10),expand=1)

        self.articleTableau = Treeview(self, columns=('date','nom','lien'),show = 'headings')
        self.articleTableau.heading('date',text='Date')
        self.articleTableau.heading('nom', text='Nom article')
        self.articleTableau.heading('lien', text='Lien')

        self.articleTableau.bind("<Double-1>", self.clicArticleTab)

        self.articleTableau.column('date',width = int(self.w/3*0.2))
        self.articleTableau.column('nom',width = int(self.w/3*1.5))
        self.articleTableau.column('lien',width = int(self.w/3*1.5 ))

        self.articleTableau.pack(padx = 10, pady = (0, 10),expand=1)

        self.geometry(str(self.w)+"x"+str(self.h))
        self.title( "Hackathon Banque de France" )



    #Tri le tableau suivant l'endroit où l'utilisateur à appuyé
    def sortTree(self,index):
        sort_list = []
        data = []
        for elem in self.tableau.get_children():
            data.append(self.tableau.item(elem)['values'])
        for elem in data:
            sort_list.append(elem[index])
        try:
            if self.sorted[0] != index or not self.sorted[1]:
                data_sorted = [x for _,x in sorted(zip(sort_list,data))]
                self.tableau.delete(*self.tableau.get_children())
                for p_i in data_sorted: 
                    self.tableau.insert('', 'end', values=tuple(p_i))
                self.sorted[0],self.sorted[1] = index,True
            else:
                data_sorted = [x for _,x in sorted(zip(sort_list,data),reverse = True)]
                self.tableau.delete(*self.tableau.get_children())
                for p_i in data_sorted: 
                    self.tableau.insert('', 'end', values=tuple(p_i))
                self.sorted[1] = False
        except:
            pass

    #Exit fonction si l'utilisateur souhaite quitter
    def press_button_exit(self):
        exit()

    #Retourne les élements présents dans les barres de recherches et le tableau de compétence
    #Sous forme d'un dictionnaire
    def search_command(self):
        name = self.name_text.get()
        institution = self.institution_text.get()
        search_dict = {}
            
        search_dict['name'] = [ elem.lower() for elem in name.strip().rsplit(" ")]
        search_dict['institution'] = [ elem.lower() for elem in institution.strip().rsplit(" ")]
        search_dict["competence"] = self.competence
        return search_dict

    def press_button_export(self):
        with open("export_economists.csv","w+") as file:
            file.write(";".join(list(self.columns_name))+"\n")
            for elem in self.tableau.get_children():
                file.write(";".join([str(value) for value in self.tableau.item(elem)['values']])+"\n")
        if self.articleTableau.get_children():
             with open("export_articles.csv","w+") as file:
                file.write(";".join(["Date","Titre","Lien"])+"\n")
                for elem in self.articleTableau.get_children():
                    file.write(";".join(self.articleTableau.item(elem)['values'])+"\n")

    #press_enter et press_bouton_enter : Lance la fonction principale de recherche avec le dictionnaire de 
    #recherche utilisateur
    def press_enter(self,event):
        self.text_presentation.configure(text = "Recherche ...")
        self.articleTableau.delete(*self.articleTableau.get_children())
        self.tableau.delete(*self.tableau.get_children())
        self.search_gestion(self.search_command())

    def press_button_enter(self):
        self.text_presentation.configure(text = "Recherche ...")
        self.articleTableau.delete(*self.articleTableau.get_children())
        self.tableau.delete(*self.tableau.get_children())
        self.search_gestion(self.search_command())

    #Nettoie le tableau, cherche les infos sur les urls, affiche les économistes
    def tab_economists(self,urls):

        if len(urls)==1:
            self.text_presentation.configure(text = "{} économiste trouvé".format(len(urls)))
        else:
            self.text_presentation.configure(text = "{} économistes trouvés\nAffichage de 100 au maximum".format(len(urls)))

        if len(urls)>100:
            urls = urls[:100]

        tab = ir.eco_perso_info_urls(urls)
        
        for p_i in tab:
            self.tableau.insert('', 'end', values=(p_i['Last Name:'],p_i['First Name:']+p_i['Middle Name:'], p_i['homelabel'],p_i['postallabel'],
                p_i['phonelabel'],p_i['Affiliations']))

    #Nettoie, charge et affiche les articles associés à l'économiste
    def tab_articles(self,urls):
        for url in urls:
            articles = ir.economist_articles(url = url)
            for nom,lien,date in zip(articles[0],articles[1],articles[2]):
                self.articleTableau.insert('','end',values=(date,nom,lien))

    #Evenement : Double clic sur un économiste, charge cet économiste et les articles
    def clicEconomistTab(self,event):
        if not self.tableau.selection():
            return
        item = self.tableau.selection()
        name = " ".join(self.tableau.item(item)['values'][:2])
        name = name.rsplit(" ")
        urls = ir.economist_url([elem.lower() for elem in name])

        self.articleTableau.delete(*self.articleTableau.get_children())
        self.tableau.delete(*self.tableau.get_children())
        
        self.tab_economists(urls)
        self.tab_articles(urls)

    #Evenement double clic sur un article, ouvre le navigateur sur l'article
    def clicArticleTab(self,event):
        if not self.articleTableau.selection():
            return
        item = self.articleTableau.selection()[0]
        addr = self.articleTableau.item(item)['values'][2]
        webbrowser.open(addr)

    #Evenement double clic sur une compétence, sauvegarde la compétence et l'affiche
    #comme étant sélectionnée 
    def clicCompetenceTab(self,event):
        if not self.competenceTableau.selection():
            return
        item = self.competenceTableau.selection()
        addr = self.competenceTableau.item(item)["values"][0]
        if addr == "None":
            self.competence = []
            self.text_competence.configure(text = 'Aucune compétence')
        else:
            self.text_competence.configure(text = '{}'.format(addr))
            self.competence = [addr]


    #Fonction principale de gestion de la recherche :
    def search_gestion(self,search_dict):

        #Recherche du nom
        if search_dict['name'][0]:
            urls = ir.economist_url(search_dict['name'])

            #Rien n'a été trouvé
            if urls==None:

                self.text_presentation.configure(text = "No economist found")


            #Un economiste a été trouvé
            elif len(urls)==1:

                self.text_presentation.configure(text="\n1 economist found\n")

                self.tab_economists(urls)
                self.tab_articles(urls)
                
            #Plusieurs economistes ont été trouvés
            else:
                self.text_presentation.configure(text = "{} economist found".format(len(urls)))
                self.tab_economists(urls)
                
        #Recherche composée d'institution et de compétence
        elif search_dict['institution'][0] and search_dict['competence']:
            
            data1 = ir.economists_from_institutions(search_dict['institution'])
            data2 = ir.economists_nep(search_dict['competence'])

            #Cas 1 : Economiste venant d'insitution et de compétence trouvé
            if data1 and data2:
                liste_economistes = []
                for elem1 in data1[1]:
                    for elem2 in data2[1]:
                        if elem1 == elem2:
                            liste_economistes.append(elem1)
                if not liste_economistes:
                    self.text_presentation.configure(text = "Aucun économiste trouvé")
                else:
                    self.tab_economists(liste_economistes)
            #Cas 2 : Economiste venant de compétence trouvé mais pas d'institution
            elif not data1 and data2:
                self.tab_economists(data2[1])
            #Cas 3 : Inverse au cas 2
            elif data1 and not data2:
                self.tab_economists(data1[1])
            #Cas 4 : Aucun économiste n'a été trouvé
            else:
                self.text_presentation.configure(text = "Aucun économiste trouvé")
                
        elif search_dict['institution'][0]:
            liste_economistes = ir.economists_from_institutions(search_dict['institution'])
            if liste_economistes:
                self.tab_economists(liste_economistes[1])
            else:
                self.text_presentation.configure(text = "Aucun économiste trouvé")
        elif search_dict['competence']:
            liste_economistes = ir.economists_nep(search_dict['competence'])
            if liste_economistes:
                self.tab_economists(liste_economistes[1])
            else:
                self.text_presentation.configure(text = "Aucun économiste trouvé")

if __name__ == "__main__":
    app = Application()
    app.mainloop()