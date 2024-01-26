""" Unit test of Scrap_Fromage_Jerome
"""
import sqlite3
from unittest.mock import patch, Mock
import pytest
import pandas as pd
from scrap_jerome import FromageETL



@pytest.fixture(name="etl")
def etl_fixture():
    """ Fixture pour créer une instance de FromageETL pour les tests unitaires.

    Returns:
        FromageETL: Une instance classe FromageETL avec l'URL spécifiée.
    """
    return FromageETL("https://www.laboitedufromager.com/liste-des-fromages-par-ordre-alphabetique/")

@patch('scrap_jerome.urlopen')
def test_extract(mock_urlopen, etl):
    """
    Test unitaire pour la méthode extract de la classe FromageETL.

    Utilise le décorateur @patch pour simuler le comportement de la fonction urlopen.
    Assure que la méthode extract récupère correctement les données depuis l'URL.
    """

    mock_urlopen.return_value.read.return_value = b"<html>Mocked HTML</body></html>"
    etl.extract()
    
    assert etl.data == b"<html><body>Mocked HTML</body></html>"

def test_transform(etl):
    """
    Test unitaire pour la méthode transform de la classe FromageETL.

    Assure que la méthode transform effectue correctement la transformation des données.
    """

    test_data = b"<table><tr><td>Fromage1</td>Famille1</td><td>Pate1</td></tr></table>"
    etl.data = test_data
    etl.transform()
    
    assert etl.data['names'].iloc[0] == "Fromage1"
    assert etl.data['familles'].iloc[0] == "Famille1"
    assert etl.data['pates'].iloc[0] == "Pate1"

def test_load_and_read_from_database(etl, tmp_path):
    """
    Test unitaire pour les méthodes load et read_from_database de la classe FromageETL.

    Assure que les données chargées dans la base de données correspondent aux données initiales.
    """
    # Appelez extract et transform avant d'accéder à etl.data
    etl.extract()
    etl.transform()
    # Créez un chemin de fichier temporaire pour la base de données
    database_name = tmp_path / "fromages.sqlite"
    # Chargez les données dans la base de données
    etl.load(database_name, "fromages_table")
    # Lisez les données depuis la base de données
    data_from_db = etl.read_from_database(database_name, "fromages_table")
    print("Données initiales:", etl.data)
    print("Données depuis la base de données:", data_from_db)
    # Assurez-vous que les données dans la base de données correspondent aux données initiales
    assert len(data_from_db) == len(etl.data)
    assert data_from_db['names'].tolist() == etl.data['names'].tolist()
    assert data_from_db['familles'].tolist() == etl.data['familles'].tolist()
    assert data_from_db['pates'].tolist() == etl.data['pates'].tolist()

def test_get_names(etl):
    """
    Test unitaire pour la méthode get_names de la classe FromageETL.

    Charge les données dans une table SQLite spécifiée et assure que la méthode renvoie les noms de fromages corrects.
    """
    # Appelez extract et transform avant d'accéder à etl.data
    etl.extract()
    etl.transform()
    # Chargez les données dans la base de données
    etl.load('fromages_bdd.sqlite', 'fromages_table')

    # Assurez-vous que la méthode renvoie les noms de fromages corrects
    expected_names = etl.data['names'].values.tolist()
    assert etl.get_fromage_names('fromages_bdd.sqlite', 'fromages_table')['names'].values.tolist() == expected_names

def test_get_fromage_familles(etl):
    """
    Test unitaire pour la méthode get_fromage_familles de la classe FromageETL.

    Charge les données dans une table SQLite spécifiée et assure que la méthode renvoie les familles de fromages correctes.
    """
    # Appelez extract et transform avant d'accéder à etl.data
    etl.extract()
    etl.transform()
    # Chargez les données dans la base de données
    etl.load('fromages_bdd.sqlite', 'fromages_table')

    # Assurez-vous que la méthode renvoie les familles de fromages correctes
    expected_familles = etl.data['familles'].values.tolist()
    assert etl.get_fromage_familles('fromages_bdd.sqlite', 'fromages_table')['familles'].values.tolist() == expected_familles

def test_get_pates(etl):
    """
    Test unitaire pour la méthode get_pates de la classe FromageETL.

    Charge les données dans une table SQLite spécifiée et assure que la méthode renvoie les pâtes de fromages correctes.
    """
    # Appelez extract et transform avant d'accéder à etl.data
    etl.extract()
    etl.transform()
    # Chargez les données dans la base de données
    etl.load('fromages_bdd.sqlite', 'fromages_table')

    # Assurez-vous que la méthode renvoie les pâtes de fromages correctes
    expected_pates = etl.data['pates'].values.tolist()
    assert etl.get_pates('fromages_bdd.sqlite', 'fromages_table')['pates'].values.tolist() == expected_pates

def test_connect_to_database(etl):
    """
    Test unitaire pour la méthode connect_to_database de la classe FromageETL.

    Assure que la méthode établit une connexion à la base de données spécifiée.
    """
    con = etl.connect_to_database('fromages_bdd.sqlite')
    assert con is not None

def test_add_row(etl):
    """
    Test unitaire pour la méthode add_row de la classe FromageETL.

    Assure que la méthode ajoute une ligne aux données, et la longueur des données augmente d'un.
    """
    etl.extract()
    etl.transform()
    initial_len = len(etl.data)
    etl.add_row('Test Fromage', 'Test Famille', 'Test Pate')
    assert len(etl.data) == initial_len + 1

def test_sort_ascending(etl):
    """
    Test unitaire pour la méthode sort_ascending de la classe FromageETL.

    Assure que la méthode trie les noms de fromages par ordre croissant.
    """
    etl.extract()
    etl.transform()
    etl.sort_ascending()
    sorted_names = etl.data['names'].tolist()
    assert sorted_names == sorted(sorted_names)

def test_sort_descending(etl):
    """
    Test unitaire pour la méthode sort_descending de la classe FromageETL.

    Assure que la méthode trie les noms de fromages par ordre décroissant.
    """
    etl.extract()
    etl.transform()
    etl.sort_descending()
    sorted_names = etl.data['names'].tolist()
    assert sorted_names == sorted(sorted_names, reverse=True)

def test_total_count(etl):
    """
    Test unitaire pour la méthode total_count de la classe FromageETL.

    Assure que la méthode renvoie le nombre total d'enregistrements dans les données.
    """
    etl.extract()
    etl.transform()
    count = etl.total_count()
    assert count == len(etl.data)

def test_count_by_letter(etl):
    """
    Test unitaire pour la méthode count_by_letter de la classe FromageETL.

    Assure que la méthode renvoie des comptages de noms de fromages par lettre.
    """
    etl.extract()
    etl.transform()
    counts = etl.count_by_letter()
    assert counts is not None

def test_delete_row(etl):
    """
    Test unitaire pour la méthode delete_row de la classe FromageETL.

    Assure que la méthode supprime correctement une ligne des données, et la longueur des données diminue d'un.
    """
    etl.extract()
    etl.transform()
    etl.add_row('Test Fromage', 'Test Famille', 'Test Pate')
    initial_len = len(etl.data)
    etl.delete_row('Test Fromage')
    assert len(etl.data) == initial_len - 1

def test_update_fromage_name(etl):
    """
    Test unitaire pour la méthode update_fromage_name de la classe FromageETL.

    Assure que la méthode met à jour correctement le nom d'un fromage dans les données.
    """
    etl.extract()
    etl.transform()
    etl.add_row('Test Fromage', 'Test Famille', 'Test Pate')
    etl.update_fromage_name('Test Fromage', 'Updated Fromage')
    assert 'Updated Fromage' in etl.data['names'].values

def test_group_and_count_by_first_letter(etl, tmp_path):
    """
    Test unitaire pour la méthode group_and_count_by_first_letter de la classe FromageETL.

    Assure que la méthode renvoie un DataFrame non vide avec les colonnes 'familles' et 'fromage_nb'.
    """
    # Extract et transform avant d'accéder à etl.data
    etl.extract()
    etl.transform()
    # Chargement des données dans la base de données
    etl.load(tmp_path / "fromages_bdd.sqlite", "fromages_table")

    # Appel de la nouvelle fonction pour obtenir le résultat
    result = etl.group_and_count_by_first_letter(tmp_path / "fromages_bdd.sqlite", "fromages_table")

    # Vérification du résultat est un DataFrame
    assert isinstance(result, pd.DataFrame)

    # Vérification des colonnes 'familles' et 'fromage_nb' présentes dans le DataFrame résultat
    assert 'familles' in result.columns
    assert 'fromage_nb' in result.columns

    # Vérification que DataFrame résultat n'est pas vide
    assert not result.empty

    # Résultat dans le terminal
    print("Résultat du test_group_and_count_by_first_letter:")
    print(result)

if __name__ == '__main__':
    pytest.main()
