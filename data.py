"""
Provides the functions for getting and manipulating
the data from the database.
"""
import mysql.connector
import os
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
    try:
        # This is how to get it out of its raw SQL database form - it is mostly not needed anymore
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
    except Exception:
        if os.path.isfile("data.csv"):
            with open("data.csv", 'r') as f:
                print("Importing all titles from the CSV file...")
                titles = [line.strip() for line in f]
            limit = len(titles) if limit is None else limit
            for i in range(int(limit)):
                yield titles[i]
        else:
            print("Could not connect to MYSQL database and could not find a CSV file.")
            exit()

if __name__ == "__main__":
    titles = [t for t in get_titles(limit=100)]
    print(titles)