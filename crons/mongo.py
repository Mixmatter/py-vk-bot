import pymongo
import os

mongo_uri = os.environ['OPENSHIFT_MONGODB_DB_URL']
client = pymongo.MongoClient(mongo_uri)
db = client['python']
colll = db['test']
post_id = colll.insert_one("hello").inserted_id
print(post_id)