"""
This module contains necessary imports for the script.
"""
import os
import timeit
import sqlite3
from datetime import datetime
from urllib.request import urlopen
from urllib.parse import urlparse
import re
from bs4 import BeautifulSoup
import requests
import pandas as pd


class FromageETL:
    """
    A class dedicated to the Extraction, Transformation, and Loading (ETL) of data
    related to cheeses. This class retrieves data from a source,
    processes it, stores it in a SQLite database, and performs various
    operations on this data.
    
    Attributes:
    - url (str): The URL from which data can be extracted.
    - data (pd.DataFrame): A pandas DataFrame containing data about cheeses.
    """
    # region Initialisation
    def __init__(self):
        """
        Initializes an instance of the FromageETL class.

        Parameters:
        - url (str): The URL from which data about cheeses will be extracted.
        """
        self.url = 'https://www.laboitedufromager.com'
        self.data = None
        self.detail = None

    def extract(self,url,frame=""):
        """
        Extracts data from the specified URL and stores it in self.data.
        """
        data = urlopen(self.url + url)
        if frame == "detail":
            self.detail = data.read()
        else:
            self.data = data.read()

    def transform(self):
        """ Transforms the extracted data into a structured pandas DataFrame.

        from the HTML table, and creating a DataFrame with columns 'fromage_names', 
        'fromage_familles', 'pates', et 'creation_date'.
        """
        soup = BeautifulSoup(self.data, 'html.parser')
        cheese_dish = soup.find('table')

        fromage_names = []
        fromage_familles = []
        pates = []

        # Database evolution
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
                    self.extract(anchor.get('href'),"detail")
                    soup = BeautifulSoup(self.detail, 'html.parser')

                    img_tag = soup.find('div', class_="woocommerce-product-gallery__image").find('a')
                    if img_tag is not None:
                        picture_path = self.download_image(img_tag.get('href'))

                    # Description
                    page_desck = soup.find('div', class_='woocommerce-product-details__short-description')
                    if page_desck is not None and page_desck.text != '':
                        desck = page_desck.text.strip()

                    # Price
                    page_price = soup.find('p', class_='price')
                    if page_price is not None and page_price.text != '':
                        page_price = page_price.find('bdi')
                        price = float(re.sub(r'[^0-9,.]', '', page_price.text.strip()).replace(',','.'))

                    # If there are reviews
                    page_review = soup.find('a', href="#reviews", class_="woocommerce-review-link")
                    if page_review is not None and page_review.text != '':
                        # Number of reviews
                        page_review = page_review.find('span')
                        review = int(re.sub(r'[^0-9]', '', page_review.text.strip()))

                        # Average rating
                        ave_g = soup.find('strong', class_="rating")
                        ave_grade = float(ave_g.text.strip().replace(',','.'))

                # endregion
                # Ignore empty lines
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
        Loads the data into a specified SQLite table.

        Parameters:
        - database_name (str): The name of the SQLite database.
        - table_name (str): The name of the table to load the data into.
        """
        con = sqlite3.connect(database_name)
        self.data.to_sql(table_name, con, if_exists="replace", index=False)
        con.close()
        return self.data

    def download_image(self,url, save_directory='pictures'):
        """Download image by URL

        Args:
            url (str): URL of the image to download
            save_directory (str, optional): Path to save. Defaults to 'pictures'.

        Returns:
            str: Complete path
        """
        # Create the directory if it does not exist
        os.makedirs(save_directory, exist_ok=True)
        try:
            filename = os.path.basename(urlparse(url).path)
            filepath = os.path.join(save_directory, filename)

            response = requests.get(url,timeout=3)
            response.raise_for_status()
            # Save the image locally
            with open(filepath, 'wb') as f:
                f.write(response.content)

            print(f"Image downloaded successfully: {filepath}")
            return filepath

        except requests.exceptions.RequestException as e:
            print(f"Error downloading image: {e}")
            return None
    # endregion

    # region Metier
    def read_from_database(self, database_name, table_name):
        """
        Lit les données à partir d'une table SQLite spécifiée.

        Parameters:
        - database_name (str): Le nom de la base de données SQLite.
        - table_name (str): Le nom de la table à lire.

        Returns:
        - pd.DataFrame: Un DataFrame contenant les données de la table.
        """
        con = sqlite3.connect(database_name)
        data_from_db = pd.read_sql_query(f"SELECT * from {table_name}", con)
        con.close()
        return data_from_db

    def get_fromage_names(self, database_name, table_name):
        """
        Récupère les noms de fromages depuis une table SQLite spécifiée.

        Parameters:
        - database_name (str): Le nom de la base de données SQLite.
        - table_name (str): Le nom de la table à interroger.

        Returns:
        - pd.DataFrame: Un DataFrame contenant la colonne 'fromage_names'.
        """
        con = sqlite3.connect(database_name)
        data_from_db = pd.read_sql_query(f"SELECT fromage_names from {table_name}", con)
        con.close()
        return data_from_db

    def get_fromage_familles(self, database_name, table_name):
        """
        Récupère les familles de fromages depuis une table SQLite spécifiée.

        Parameters:
        - database_name (str): Le nom de la base de données SQLite.
        - table_name (str): Le nom de la table à interroger.

        Returns:
        - pd.DataFrame: Un DataFrame contenant la colonne 'fromage_familles'.
        """
        con = sqlite3.connect(database_name)
        data_from_db = pd.read_sql_query(f"SELECT fromage_familles from {table_name}", con)
        con.close()
        return data_from_db

    def get_pates(self, database_name, table_name):
        """
        Récupère les types de pâtes des fromages depuis une table SQLite spécifiée.

        Parameters:
        - database_name (str): Le nom de la base de données SQLite.
        - table_name (str): Le nom de la table à interroger.

        Returns:
        - pd.DataFrame: Un DataFrame contenant la colonne 'pates'.
        """
        con = sqlite3.connect(database_name)
        data_from_db = pd.read_sql_query(f"SELECT pates from {table_name}", con)
        con.close()
        return data_from_db

    def connect_to_database(self, database_name):
        """
        Établit une connexion à une base de données SQLite.

        Parameters:
        - database_name (str): Le nom de la base de données SQLite.

        Returns:
        - sqlite3.Connection: Objet de connexion à la base de données.
        """
        con = sqlite3.connect(database_name)
        return con

    def add_row(self, fromage_name, fromage_famille, pate):
        """
        Ajoute une nouvelle ligne à l'ensemble de données avec les informations spécifiées.

        Parameters:
        - fromage_name (str): Nom du fromage à ajouter.
        - fromage_famille (str): Famille du fromage à ajouter.
        - pate (str): Type de pâte du fromage à ajouter.
        """
        new_row = pd.DataFrame({'fromage_names': [fromage_name],
            'fromage_familles': [fromage_famille], 'pates': [pate]})
        self.data = pd.concat([self.data, new_row], ignore_index=True)

    def sort_ascending(self):
        """
        Trie l'ensemble de données par ordre croissant des noms de fromages.
        """
        self.data = self.data.sort_values(by=['fromage_names'])

    def sort_descending(self):
        """
        Trie l'ensemble de données par ordre décroissant des noms de fromages.
        """
        self.data = self.data.sort_values(by=['fromage_names'], ascending=False)

    def total_count(self):
        """
        Retourne le nombre total de lignes dans l'ensemble de données.

        Returns:
        - int: Nombre total de lignes.
        """
        return len(self.data)

    def count_by_letter(self):
        """
        Compte le nombre de fromages par lettre initiale dans les noms.

        Returns:
        - pd.Series: Série contenant le décompte des fromages par lettre initiale.
        """
        return self.data['fromage_names'].str[0].value_counts()

    def update_fromage_name(self, old_name, new_name):
        """
        Met à jour le nom d'un fromage dans l'ensemble de données.

        Parameters:
        - old_name (str): Ancien nom du fromage à mettre à jour.
        - new_name (str): Nouveau nom à attribuer au fromage.
        """
        self.data.loc[self.data.fromage_names == old_name, 'fromage_names'] = new_name

    def delete_row(self, fromage_name):
        """
        Supprime une ligne de l'ensemble de données basée sur le nom du fromage.

        Parameters:
        - fromage_name (str): Nom du fromage à supprimer.
        """
        self.data = self.data[self.data.fromage_names != fromage_name]

    def group_and_count_by_first_letter(self, database_name, table_name):
        """
        Regroupe les fromages par la première lettre de la famille,
        et compte le nombre de fromages par groupe.

        Parameters:
        - database_name (str): Le nom de la base de données SQLite.
        - table_name (str): Le nom de la table à interroger.

        Returns:
        - pd.DataFrame: Un DataFrame contenant les colonnes 'fromage_familles' et 'fromage_nb'.
        """
        # Utilisez la fonction get_fromage_familles pour récupérer les familles de fromages
        data_from_db = self.get_fromage_familles(database_name, table_name)

        # Créez une nouvelle colonne 'lettre_alpha'
        data_from_db['lettre_alpha'] = data_from_db['fromage_familles'].str[0]

        # Utilisez groupby 'fromage_familles' et compter nb_fromages
        grouped_data = data_from_db.groupby('fromage_familles').size().reset_index(name='fromage_nb')

        return grouped_data

# starttime = timeit.default_timer()
# fromage_etl = FromageETL()
# fromage_etl.extract('/liste-des-fromages-par-ordre-alphabetique/')
# fromage_etl.transform()
# fromage_etl.load('fromages_bdd.sqlite', 'fromages_table')
# print((timeit.default_timer() - starttime)/60)
