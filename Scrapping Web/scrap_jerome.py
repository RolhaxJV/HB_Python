""" Scrapping web """
from datetime import datetime
import sqlite3
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd



class FromageETL:
    """_summary_
    """
    def __init__(self, url):
        self.url = url
        self.data = None

    def extract(self):
        """_summary_
        """
        data = urlopen(self.url)
        self.data = data.read()

    def transform(self):
        """_summary_
        """
        soup = BeautifulSoup(self.data, 'html.parser')
        cheese_dish = soup.find('table')

        fromage_names = []
        fromage_familles = []
        pates = []

        for row in cheese_dish.find_all('tr'):
            columns = row.find_all('td')

            if(columns[0].text.strip() == "Fromage"):
                continue
            
            if columns:
                fromage_name = columns[0].text.strip()
                fromage_famille = columns[1].text.strip()
                pate = columns[2].text.strip()

                # Ignore les lignes vides
                if fromage_name != '' and fromage_famille != '' and pate != '':
                    fromage_names.append(fromage_name)
                    fromage_familles.append(fromage_famille)
                    pates.append(pate)

        self.data = pd.DataFrame({
            'names': fromage_names,
            'familles': fromage_familles,
            'pates': pates
        })

        self.data['creation_date'] = datetime.now()

    def load(self, database_name, table_name):
        """_summary_

        Args:
            database_name (_type_): _description_
            table_name (_type_): _description_
        """
        con = sqlite3.connect(database_name)
        self.data.to_sql(table_name, con, if_exists="replace", index=False)
        con.close()

    def read_from_database(self, database_name, table_name,group_by=False):
        """_summary_

        Args:
            database_name (_type_): _description_
            table_name (_type_): _description_

        Returns:
            _type_: _description_
        """

        con = sqlite3.connect(database_name)
        
        if group_by:
            data_db = pd.read_sql_query(f"SELECT familles, Count(*) as nb_f from {table_name} group by familles", con)
        else:
            data_db = pd.read_sql_query(f"SELECT * from {table_name} ", con) 
        
        con.close()
        return data_db

# Utilisation de la classe
fromage_etl = FromageETL('https://www.laboitedufromager.com/liste-des-fromages-par-ordre-alphabetique/')
fromage_etl.extract()
fromage_etl.transform()
fromage_etl.load('fromages_bdd.sqlite', 'fromages_table')
print(fromage_etl.read_from_database('fromages_bdd.sqlite', 'fromages_table'))
print(fromage_etl.read_from_database('fromages_bdd.sqlite', 'fromages_table',True))


