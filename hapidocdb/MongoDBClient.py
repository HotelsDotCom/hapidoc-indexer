"""
Copyright (C) 2018 Expedia Group.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


class MongoDBClient:
    """
    Performs db actions such as creating collections, inserting documents into them, and deleting collections.
    """

    def __init__(self, client, db):
        """
        Instantiates a mongo db client, given a MongoClient and a db instance.
        :param client: a MongoClient object
        :param db: a mongodb instance
        """
        self.mongo_client = client
        self.db = db

    def populate_collection(self, collection, docs):
        """
        Inserts a list of documents into a given collection, if collection exists. Otherwise, it creates the collection.
        :param collection: the name of the collection
        :param docs: a list of mongodb documents
        """
        self.db[collection].insert_many(docs)

    def delete_collection(self, collection):
        """
        Deletes a collection (if it exists).
        :param collection: the name of the collection
        """
        self.db[collection].remove({})
