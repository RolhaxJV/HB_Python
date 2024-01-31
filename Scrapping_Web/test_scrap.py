"""
Module de tests pour le script scrapping_fromage.py

Ce module contient des tests unitaires pour la classe FromageETL du script scrapping_fromage.py.
Les tests sont écrits en utilisant le framework de test pytest.

Avertissement:
- Ce module nécessite l'installation de pandas et pytest.
- Certains tests utilisent la fonction patch du module unittest.mock
pour simuler le comportement de certaines fonctions.

Usage:
- Exécutez le script en utilisant pytest pour exécuter tous les tests définis dans ce module.

Exemple:
    pytest -s test_scrapping_fromages.py
"""
# test_scrapping_fromages.py
from unittest.mock import patch, Mock
import pandas as pd
import pytest


from scrap_jerome import FromageETL

@pytest.fixture(name="etl_instance")
def etl_instance_fixture():
    """
    Fixture pour créer une instance de FromageETL pour les tests unitaires.

    Returns:
    - FromageETL: Une instance classe FromageETL avec l'URL spécifiée.
    """
    return FromageETL()

@patch('scrap_jerome.urlopen')
def test_extract(mock_urlopen, etl_instance):
    """
    Test unitaire pour la méthode extract de la classe FromageETL.

    Utilise le décorateur @patch pour simuler le comportement de la fonction urlopen.
    Assure que la méthode extract récupère correctement les données depuis l'URL.
    """
    # Configurez le comportement simulé de urlopen
    mock_urlopen.return_value.read.return_value = b"<html><body>Mocked HTML</body></html>"
    # Appelez la méthode extract
    etl_instance.extract('/liste-des-fromages-par-ordre-alphabetique/')
    # Assurez-vous que les données ont été correctement extraites
    assert etl_instance.data == b"<html><body>Mocked HTML</body></html>"

def test_transform(etl_instance):
    """
    Test unitaire pour la méthode transform de la classe FromageETL.

    Assure que la méthode transform effectue correctement la transformation des données.
    """
    # Définissez les données de test
    test_data = b"<table><tr><td>Fromage1</td><td>Famille1</td><td>Pate1</td></tr></table>"
    etl_instance.data = test_data
    # Appelez la méthode transform
    etl_instance.transform()
    # Assurez-vous que les données ont été correctement transformées
    assert etl_instance.data['fromage_names'].iloc[0] == "Fromage1"
    assert etl_instance.data['fromage_familles'].iloc[0] == "Famille1"
    assert etl_instance.data['pates'].iloc[0] == "Pate1"

def test_load_and_read_from_database(etl_instance, tmp_path):
    """
    Test unitaire pour les méthodes load et read_from_database de la classe FromageETL.

    Assure que les données chargées dans la base de données correspondent aux données initiales.
    """
    # Appelez extract et transform avant d'accéder à etl_instance.data
    etl_instance.extract('/liste-des-fromages-par-ordre-alphabetique/')
    etl_instance.transform()
    # Créez un chemin de fichier temporaire pour la base de données
    database_name = tmp_path / "fromages.sqlite"
    # Chargez les données dans la base de données
    etl_instance.load(database_name, "fromages_table")
    # Lisez les données depuis la base de données
    data_from_db = etl_instance.read_from_database(database_name, "fromages_table")
    print("Données initiales:", etl_instance.data)
    print("Données depuis la base de données:", data_from_db)
    # Assurez-vous que les données dans la base de données correspondent aux données initiales
    assert len(data_from_db) == len(etl_instance.data)
    assert data_from_db['fromage_names'].tolist() == etl_instance.data['fromage_names'].tolist()
    assert data_from_db['fromage_familles'].tolist() == etl_instance.data['fromage_familles'].tolist()
    assert data_from_db['pates'].tolist() == etl_instance.data['pates'].tolist()

def test_get_fromage_names(etl_instance):
    """
    Test unitaire pour la méthode get_fromage_names de la classe FromageETL.

    Charge les données dans une table SQLite spécifiée 
    et assure que la méthode renvoie les noms de fromages corrects.
    """
    # Appelez extract et transform avant d'accéder à etl_instance.data
    etl_instance.extract('/liste-des-fromages-par-ordre-alphabetique/')
    etl_instance.transform()
    # Chargez les données dans la base de données
    etl_instance.load('fromages_bdd.sqlite', 'fromages_table')

    # Assurez-vous que la méthode renvoie les noms de fromages corrects
    expected_names = etl_instance.data['fromage_names'].values.tolist()
    assert etl_instance.get_fromage_names('fromages_bdd.sqlite',
        'fromages_table')['fromage_names'].values.tolist() == expected_names

def test_get_fromage_familles(etl_instance):
    """
    Test unitaire pour la méthode get_fromage_familles de la classe FromageETL.

    Charge les données dans une table SQLite spécifiée
    et assure que la méthode renvoie les familles de fromages correctes.
    """
    # Appelez extract et transform avant d'accéder à etl_instance.data
    etl_instance.extract('/liste-des-fromages-par-ordre-alphabetique/')
    etl_instance.transform()
    # Chargez les données dans la base de données
    etl_instance.load('fromages_bdd.sqlite', 'fromages_table')

    # Assurez-vous que la méthode renvoie les familles de fromages correctes
    expected_familles = etl_instance.data['fromage_familles'].values.tolist()
    assert etl_instance.get_fromage_familles('fromages_bdd.sqlite',
        'fromages_table')['fromage_familles'].values.tolist() == expected_familles

def test_get_pates(etl_instance):
    """
    Test unitaire pour la méthode get_pates de la classe FromageETL.

    Charge les données dans une table SQLite spécifiée
    et assure que la méthode renvoie les pâtes de fromages correctes.
    """
    # Appelez extract et transform avant d'accéder à etl_instance.data
    etl_instance.extract('/liste-des-fromages-par-ordre-alphabetique/')
    etl_instance.transform()
    # Chargez les données dans la base de données
    etl_instance.load('fromages_bdd.sqlite', 'fromages_table')

    # Assurez-vous que la méthode renvoie les pâtes de fromages correctes
    expected_pates = etl_instance.data['pates'].values.tolist()
    assert etl_instance.get_pates('fromages_bdd.sqlite',
        'fromages_table')['pates'].values.tolist() == expected_pates

def test_connect_to_database(etl_instance):
    """
    Test unitaire pour la méthode connect_to_database de la classe FromageETL.

    Assure que la méthode établit une connexion à la base de données spécifiée.
    """
    con = etl_instance.connect_to_database('fromages_bdd.sqlite')
    assert con is not None

def test_add_row(etl_instance):
    """
    Test unitaire pour la méthode add_row de la classe FromageETL.

    Assure que la méthode ajoute une ligne aux données, et la longueur des données augmente d'un.
    """
    etl_instance.extract('/liste-des-fromages-par-ordre-alphabetique/')
    etl_instance.transform()
    initial_len = len(etl_instance.data)
    etl_instance.add_row('Test Fromage', 'Test Famille', 'Test Pate')
    assert len(etl_instance.data) == initial_len + 1

def test_sort_ascending(etl_instance):
    """
    Test unitaire pour la méthode sort_ascending de la classe FromageETL.

    Assure que la méthode trie les noms de fromages par ordre croissant.
    """
    etl_instance.extract('/liste-des-fromages-par-ordre-alphabetique/')
    etl_instance.transform()
    etl_instance.sort_ascending()
    sorted_names = etl_instance.data['fromage_names'].tolist()
    assert sorted_names == sorted(sorted_names)

def test_sort_descending(etl_instance):
    """
    Test unitaire pour la méthode sort_descending de la classe FromageETL.

    Assure que la méthode trie les noms de fromages par ordre décroissant.
    """
    etl_instance.extract('/liste-des-fromages-par-ordre-alphabetique/')
    etl_instance.transform()
    etl_instance.sort_descending()
    sorted_names = etl_instance.data['fromage_names'].tolist()
    assert sorted_names == sorted(sorted_names, reverse=True)

def test_total_count(etl_instance):
    """
    Test unitaire pour la méthode total_count de la classe FromageETL.

    Assure que la méthode renvoie le nombre total d'enregistrements dans les données.
    """
    etl_instance.extract('/liste-des-fromages-par-ordre-alphabetique/')
    etl_instance.transform()
    count = etl_instance.total_count()
    assert count == len(etl_instance.data)

def test_count_by_letter(etl_instance):
    """
    Test unitaire pour la méthode count_by_letter de la classe FromageETL.

    Assure que la méthode renvoie des comptages de noms de fromages par lettre.
    """
    etl_instance.extract('/liste-des-fromages-par-ordre-alphabetique/')
    etl_instance.transform()
    counts = etl_instance.count_by_letter()
    assert counts is not None

def test_delete_row(etl_instance):
    """
    Test unitaire pour la méthode delete_row de la classe FromageETL.

    Assure que la méthode supprime correctement une ligne des données,
    et la longueur des données diminue d'un.
    """
    etl_instance.extract('/liste-des-fromages-par-ordre-alphabetique/')
    etl_instance.transform()
    etl_instance.add_row('Test Fromage', 'Test Famille', 'Test Pate')
    initial_len = len(etl_instance.data)
    etl_instance.delete_row('Test Fromage')
    assert len(etl_instance.data) == initial_len - 1

def test_update_fromage_name(etl_instance):
    """
    Test unitaire pour la méthode update_fromage_name de la classe FromageETL.

    Assure que la méthode met à jour correctement le nom d'un fromage dans les données.
    """
    etl_instance.extract('/liste-des-fromages-par-ordre-alphabetique/')
    etl_instance.transform()
    etl_instance.add_row('Test Fromage', 'Test Famille', 'Test Pate')
    etl_instance.update_fromage_name('Test Fromage', 'Updated Fromage')
    assert 'Updated Fromage' in etl_instance.data['fromage_names'].values

def test_group_and_count_by_first_letter(etl_instance, tmp_path):
    """
    Test unitaire pour la méthode group_and_count_by_first_letter de la classe FromageETL.

    Assure que la méthode renvoie un DataFrame non vide
    avec les colonnes 'fromage_familles' et 'fromage_nb'.
    """
    # Extract et transform avant d'accéder à etl_instance.data
    etl_instance.extract('/liste-des-fromages-par-ordre-alphabetique/')
    etl_instance.transform()
    # Chargement des données dans la base de données
    etl_instance.load(tmp_path / "fromages_bdd.sqlite", "fromages_table")

    # Appel de la fonction pour obtenir le résultat
    result = etl_instance.group_and_count_by_first_letter(tmp_path / "fromages_bdd.sqlite", "fromages_table")

    # Vérification du résultat est un DataFrame
    assert isinstance(result, pd.DataFrame)

    # Vérification des colonnes 'fromage_familles' et 'fromage_nb'
    assert 'fromage_familles' in result.columns
    assert 'fromage_nb' in result.columns

    # Vérification que DataFrame résultat n'est pas vide
    assert not result.empty

    # Résultat dans le terminal
    print("Résultat du test_group_and_count_by_first_letter:")
    print(result)

if __name__ == '__main__':
    pytest.main()