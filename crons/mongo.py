import pymongo
import os

mongo_uri = os.eniron['OPENSHIFT_MONGODB_DB_URL']
client = pymongo.MongoClient(mongo_uri)
db = client['python']
print(db.collection_names())