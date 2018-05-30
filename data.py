"""
Provides the functions for getting and manipulating
the data from the database.
"""
import mysql.connector
import yaml

def _read_secret_file():
    """
    Reads the configuration for the database and returns it
    as a dict.
    """
    with open("secret.yml", 'r') as f:
        return yaml.load(f)

def get_titles(limit=None):
    """
    Yields the titles from the database, one title at a time.
    """
    config = _read_secret_file()
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT * FROM titles" if limit is None else "SELECT * FROM titles LIMIT {}".format(int(limit))
    cursor.execute(query)
    for cols in cursor:
        title = cols[1]
        yield title
    cursor.close()
    cnx.close()

if __name__ == "__main__":
    titles = [t for t in get_titles(limit=100)]
    print(titles)