"""
Script to take the data out of the SQL database and
stick it into CSV.
"""
import data

if __name__ == "__main__":
    with open("data.csv", 'w') as f:
        all_titles = "\n".join([t for t in data.get_titles()])
        f.write(all_titles + "\n")
