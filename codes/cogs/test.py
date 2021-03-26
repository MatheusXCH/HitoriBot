import json
import os
import pprint
import random
from pprint import pprint

import asyncpraw
import codes.settings as st
import dotenv
import mal
import pandas
import requests
from dotenv import load_dotenv
from google_trans_new import google_translator
from howlongtobeatpy import HowLongToBeat
from jikanpy import Jikan
from riotwatcher import ApiError, LolWatcher
from roleidentification import *
from pymongo import MongoClient

# load_dotenv()
# CONNECT_STRING = os.getenv("MONGO_CONNECT_STRING")

# client = MongoClient(CONNECT_STRING)

# # print(client.list_database_names())

# db = client.get_database(name="discordzada")
# collection = db.get_collection(name="free-game-findings-channels")

# data = {"name": "Test", "email": "TESTANDO_MUITO@Test.com", "phone": "1299999999"}
# data2 = {"name": "Test2", "email": "Test2@Test2.com", "phone": "1289999999"}

# collection.update_one({"name": data["name"]}, {"$set": data}, upsert=True)
