#!/bin/python3

import vk
from pymongo import MongoClient
import os

mongo_db_url = os.environ['OPENSHIFT_MONGODB_DB_URL']

client = MongoClient(mongo_db_url)
db = client["python"]
coll = db["testing"]

import random
coll.insert_one(random.random())