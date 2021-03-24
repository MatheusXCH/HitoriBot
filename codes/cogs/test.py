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

# load_dotenv()
# reddit = asyncpraw.Reddit(
#                     client_id = os.getenv('PRAW_CLIENT_ID'),
#                     client_secret = os.getenv('PRAW_CLIENT_SECRET'),
#                     username = os.getenv('PRAW_USERNAME'),
#                     password = os.getenv('PRAW_PASSWORD'),
#                     user_agent = os.getenv('PRAW_USER_AGENT')
#                     )

# async def test(subreddit):
#     await print(subreddit.name)

# async def main():
#     subreddit = await reddit.subreddit('FreeGameFindings')
#     call = await test(subreddit)
#     await call.close()

response_riot = requests.get("https://127.0.0.1:2999/liveclientdata/allgamedata")
riot_json = response_riot.json()
pprint(riot_json)
