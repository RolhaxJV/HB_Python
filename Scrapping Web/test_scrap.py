""" Unit test of Scrap_Fromage_Jerome
"""
import os
import pytest
import pandas as pd
from scrap_jerome import FromageETL



@pytest.fixture(name="etl")
def etl_fixture():
    """ instance of a FromageETL object 

    Returns:
        FromageETL: FromageETL object
    """
    return FromageETL('https://www.laboitedufromager.com/liste-des-fromages-par-ordre-alphabetique/')

def test_extract(etl):
    """ Check extract()

    Args:
        etl (FromageETL): FromageETL object
    """
    etl.extract()
    assert etl.data is not None


def test_load(etl):
    """ Check load()

    Args:
        etl (FromageETL): FromageETL object
    """
    etl.data = pd.DataFrame({'names': ['Cheddar'], 'familles': ['Fromage dur'], 'pates': ['Dur']})
    etl.load('fromages_bdd.sqlite', 'fromages_table')
    assert os.path.exists("fromages_bdd.sqlite")

def test_read_from_database(etl):
    """ Check read_from_database()

    Args:
        etl (FromageETL): FromageETL object
    """
    etl.data = pd.DataFrame({'names': ['Cheddar'], 'familles': ['Fromage dur'], 'pates': ['Dur']})
    etl.load('fromages_bdd.sqlite', 'fromages_table')
    data_from_db = etl.read_from_database('fromages_bdd.sqlite', 'fromages_table')
    assert len(data_from_db) == 1


def test_invalid_url(etl):
    """ Check invalid_url()

    Args:
        etl (FromageETL): FromageETL object
    """
    etl.url = 'invalid_url'
    with pytest.raises(Exception):
        etl.extract()

def test_empty_data_after_transform(etl):
    """ Check if data is empty after transform()

    Args:
        etl (FromageETL): FromageETL object
    """
    etl.data = b'<table></table>'
    etl.transform()
    assert len(etl.data) == 0

def test_empty_database_table(etl):
    """ Check the database

    Args:
        etl (FromageETL): FromageETL object
    """
    etl.extract()
    etl.transform()
    etl.load('fromages_bdd.sqlite', 'fromages_table')
    data_from_db = etl.read_from_database('fromages_bdd.sqlite', 'fromages_table')
    assert len(data_from_db) != 0
