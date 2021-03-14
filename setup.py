import argparse
from glob import glob

from database import Database
from file import File
from yaml import Yaml

parser = argparse.ArgumentParser()
parser.add_argument("-db", type=str, help="Path to db file", default="database.db")
args = parser.parse_args()

db = Database(args.db)
for file in glob("initial_data/*"):
    db.exec(File(file).get_content())
