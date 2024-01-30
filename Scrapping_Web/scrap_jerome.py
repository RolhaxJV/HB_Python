"""
Ce module contient les importations nécessaires pour le script.
"""
import os
import timeit
import sqlite3
from datetime import datetime
from urllib.request import urlopen
from urllib.parse import urljoin
from urllib.parse import urlparse
import re
from bs4 import BeautifulSoup
import requests
import pandas as pd


class FromageETL:
    """
    Une classe dédiée à l'extraction, la transformation et le chargement (ETL) de données
    relatives aux fromages. Cette classe permet de récupérer des données depuis une source,
    de les traiter, de les stocker dans une base de données SQLite, et d'effectuer diverses
    opérations sur ces données.
    
    Attributes :
    - url (str) : L'URL à partir de laquelle les données peuvent être extraites.
    - data (pd.DataFrame) : Un DataFrame pandas contenant les données sur les fromages.
    """

    def __init__(self, url):
        """
        Initialise une instance de la classe FromageETL.

        Parameters:
        - url (str): L'URL à partir de laquelle les données sur les fromages seront extraites.
        """
        self.url = url
        self.data = None
        self.detail = None

    def extract(self,frame=""):
        """
        Extrait les données à partir de l'URL spécifiée et les stocke dans self.data.
        """
        data = urlopen(self.url)
        if(frame == "detail"):
            self.detail = data.read() 
        else:
            self.data = data.read()

    def transform(self):
        """
        Transforme les données extraites en un DataFrame pandas structuré.

        Le processus implique l'analyse HTML des données,
        la récupération des informations sur les fromages
        à partir de la table HTML, et la création d'un DataFrame avec les colonnes 'fromage_names', 
        'fromage_familles', 'pates', et 'creation_date'.
        """
        soup = BeautifulSoup(self.data, 'html.parser')
        cheese_dish = soup.find('table')

        fromage_names = []
        fromage_familles = []
        pates = []

        # evolution de la base
        pictures_paths = []
        prices = []
        descks = []
        average_grades = []
        nb_reviews = []

        for row in cheese_dish.find_all('tr'):
            columns = row.find_all('td')

            if columns[0].text.strip() == "Fromage":
                continue

            if columns:
                fromage_name = columns[0].text.strip()
                fromage_famille = columns[1].text.strip()
                pate = columns[2].text.strip()

                # region Evolution
                picture_path = None
                price = None
                desck = None
                ave_grade = None
                review = None

                anchor = columns[0].find('a')
                if anchor:
                    href = anchor.get('href')
                    full_url = "https://www.laboitedufromager.com/" + href
                    data = urlopen(full_url)
                    self.detail = data.read()
                    soup = BeautifulSoup(self.detail, 'html.parser')

                    img_tag = soup.find('div', class_="woocommerce-product-gallery__image").find('a')
                    if img_tag is not None:
                        # Convertit l'URL relative en URL absolue
                        picture_path = self.download_image(img_tag.get('href'))

                    # Description
                    page_desck = soup.find('div', class_='woocommerce-product-details__short-description')
                    if page_desck is not None and page_desck.text != '':
                        desck = page_desck.text.strip()

                    # Prix
                    page_price = soup.find('p', class_='price')
                    if page_price is not None and page_price.text != '':
                        page_price.find('bdi')
                        price = float(re.sub(r'[^0-9,]', '', page_price.text.strip()).replace(',','.'))

                    # Si il y a des avis
                    page_review = soup.find('a', href="#reviews", class_="woocommerce-review-link")
                    if page_review is not None and page_review.text != '':
                        # Nombre d'avis
                        page_review.find('span')
                        review = int(re.sub(r'[^0-9,]', '', page_review.text.strip()))

                        # Moyenne de notation
                        ave_g = soup.find('strong', class_="rating")
                        ave_grade = float(ave_g.text.strip().replace(',','.'))

                # endregion
                # Ignore les lignes vides
                if fromage_name != '' and fromage_famille != '' and pate != '':
                    fromage_names.append(fromage_name)
                    fromage_familles.append(fromage_famille)
                    pates.append(pate)

                    pictures_paths.append(picture_path)
                    prices.append(price)
                    descks.append(desck)
                    average_grades.append(ave_grade)
                    nb_reviews.append(review)

        self.data = pd.DataFrame({
            'fromage_names': fromage_names,
            'fromage_familles': fromage_familles,
            'pates': pates,
            'pictures_paths' : pictures_paths,
            'prices' : prices,
            'descriptions' : descks,
            'grades' : average_grades,
            'reviews_number': nb_reviews
        })

        self.data['creation_date'] = datetime.now()

    def load(self, database_name, table_name):
        """
        Charge les données dans une table SQLite spécifiée.

        Parameters:
        - database_name (str): Le nom de la base de données SQLite.
        - table_name (str): Le nom de la table dans laquelle charger les données.
        """
        con = sqlite3.connect(database_name)
        self.data.to_sql(table_name, con, if_exists="replace", index=False)
        con.close()
        return self.data

    def download_image(self,url, save_directory='pictures'):
        """ Download image by url

        Args:
            url (str): url of the image to download
            save_directory (str, optional): path to save. Defaults to 'pictures'.

        Returns:
            str: complet path
        """
        # Crée le répertoire s'il n'existe pas
        os.makedirs(save_directory, exist_ok=True)
        try:
            filename = os.path.basename(urlparse(url).path)
            filepath = os.path.join(save_directory, filename)

            response = requests.get(url)
            response.raise_for_status()
            # Enregistre l'image localement
            with open(filepath, 'wb') as f:
                f.write(response.content)

            print(f"Image téléchargée avec succès : {filepath}")
            return filepath

        except requests.exceptions.RequestException as e:
            print(f"Erreur lors du téléchargement de l'image : {e}")
            return None

starttime = timeit.default_timer()
# Utilisation de la classe
A = 'https://www.laboitedufromager.com/liste-des-fromages-par-ordre-alphabetique/'
fromage_etl = FromageETL(A)
fromage_etl.extract()
fromage_etl.transform()
fromage_etl.load('fromages_bdd.sqlite', 'fromages_table')
print((timeit.default_timer() - starttime)/60)
