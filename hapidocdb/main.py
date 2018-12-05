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

import os
import sys
sys.path.insert(0, os.path.pardir)
import requests

from pymongo import MongoClient

from MongoDBClient import MongoDBClient
from helper import create_documents
from mappings import projects_map


def main():
    os.chdir("/hapidocindexer/hapidocdb")

    mongodb_host = os.environ['MONGO_DB_HOST']
    mongodb_port = int(os.environ['MONGO_DB_PORT'])
    web_host = os.environ['HAPIDOC_WEB_HOST']
    web_port = os.environ['HAPIDOC_WEB_PORT']
    web_pass = os.environ['HAPIDOC_WEB_PASS']
    bitbucket_host = os.environ['BITBUCKET_HOST']

    # open db connection
    print "Opening connection...\n"
    client = MongoClient(mongodb_host, mongodb_port)
    db_name = 'hapidocdb'
    db = client[db_name]
    mongodb_client = MongoDBClient(client, db)

    # insert documents into collections
    print "Collections indexing started..."
    for collection in projects_map:
        print "Indexing " + collection + "..."
        mongodb_client.delete_collection(collection)
        docs = create_documents(collection, bitbucket_host)
        mongodb_client.populate_collection(collection, docs)
    print "Collections indexing has finished!\n"

    # close connection
    print "Closing connection...\n"
    client.close()

    print "Sending post request to refresh web server..."
    web_uri = web_host
    if web_port:
        web_uri += ':' + web_port
    r = requests.post(web_uri + '/refresh', json={"pass": web_pass})
    print r.status_code, r.reason


if __name__ == '__main__':
    main()
