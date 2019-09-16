import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
from bs4 import BeautifulSoup
import re
import pandas as pd
from urllib.request import urlopen, Request
import threading


def thread_parallele(procedure):
        """lance la procédure dans un procédure parallèle"""
        thread=threading.Thread(name='Thread_parallele',target=procedure)
        thread.start()
def liste_annonce(url, filename = 'annonces'):
    """méthode qui permet de regroupe les annonces d'un page seloger.com dans un dataframe"""
    #initalisation du dataframe
    df_master = pd.DataFrame()
    #initialise l'increment
    inc = 1
    #code source de la page
    hd = {'User-Agent': 'Chrome'}
    while True:
        url_target = url  + '&LISTING-LISTpg=' + str(inc)
        data =urlopen(Request(url_target, headers=hd)).read()
        #interpretation du code source avec BS
        soup = BeautifulSoup(data)
        #liste des tags script
        result =soup.find_all('script')
        #recherche du tag contenant les données sur l'immobilier
        for tag in result:
            for content in tag.stripped_strings:
                if re.match('^var ava_data*',content):
                    new_c =content
        #mise en forme des informations
        new_c = new_c.replace('\r\n','')
        new_c = new_c.replace('  ','')
        new_c = new_c.replace('var ava_data = ','')
        new_c = new_c.replace(';ava_data.logged = logged;','')
        #création d'un dictionnaire à partir du string
        dic = json.loads(new_c)
        #creation du dataframe
        df = pd.DataFrame(dic['products'])
        #supprime les annonces vides
        if 'idannonce' in df.columns:
            df = df.loc[df['idannonce'].notnull()]
        else:
            break
        df['surface'] = df['surface'].str.replace(',','.')
        #modifie le type de donnée
        df = df.astype({'position' :'int32','codepostal':'int32',
                            'codeinsee' :'int32', 'cp' : 'int32', 'etage' : 'int32', 
                            'idtypechauffage' : 'int32','idtypecommerce': 'int32',
                            'naturebien' : 'int32','si_balcon' : 'int32', 'nb_chambres' : 'int32', 
                            'nb_pieces' : 'int32', 'si_sdbain' : 'int32', 'si_sdEau' : 'int32','nb_photos' : 'int32',
                            'prix' : 'float', 'surface' : 'float',
                           })
        if not df.empty:
            df_master = pd.concat([df_master,df], sort = False)
            inc +=1
        else:
            break
    df_master.to_excel(filename +'.xlsx', index = False)
    messagebox.showinfo('Fichier créé', 'Le fichier %s a été créé' %(filename))

fenetre = tk.Tk()
fenetre.title('Gestionnaire')

#label url
label_url= ttk.Label(fenetre, text="Veuillez entrer l'url",width = 100)
label_url.grid(row=0, column=0,padx=0,pady=0)
#texte url
entry_url = ttk.Entry(fenetre, width = 100)
entry_url.grid(row=1, column=0, padx=5,pady=5)
#label nom fichier
label_fichier= ttk.Label(fenetre, text="Nom du fichier de sortie",width = 50)
label_fichier.grid(row=2, column=0,padx=0,pady=0)
#texte nom de fichier
f = tk.StringVar()
f.set('annonces')
entry_fichier = ttk.Entry(fenetre, width = 50,textvariable=f,)
entry_fichier.grid(row=3, column=0, padx=5,pady=5)

#bouton lancement
Bouton_lancement = ttk.Button(fenetre,width = 40,text= 'Créer la liste des annonces',
                            command = lambda: thread_parallele(liste_annonce(entry_url.get(),entry_fichier.get())))
Bouton_lancement.grid(row=4, column=0,padx=5,pady=5)

fenetre.mainloop()
