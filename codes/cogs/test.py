import os, mal, dotenv
from dotenv import load_dotenv
from jikanpy import Jikan

from google_trans_new import google_translator
from howlongtobeatpy import HowLongToBeat

import random, pandas, pprint
from pprint import pprint
from riotwatcher import LolWatcher, ApiError

import json
import requests
import codes.settings as st

from roleidentification import *

import asyncpraw

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
