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
import re
import sys

sys.path.insert(0, os.path.pardir)
import time

from HoundClient import HoundClient
from BitBucketServerClient import BitBucketServerClient
from mappings import projects_map
import helper


class HoundPreprocessor:
    """
    This preprocessor creates the dataset for CLAMS by using Hound to filter down to specific files.
    """

    def __init__(self, call_name, client_name):
        """
        Instantiates a HoundPreprocessor, and sets local variables based on environment ones.
        :param call_name: regex that call filename should match
        :param client_name: regex that client filename should match
        """
        self.bitbucket_host = os.environ['BITBUCKET_HOST']
        self.hound_host = os.environ['HOUND_HOST']
        self.is_bitbucket_ssh = os.environ['IS_BITBUCKET_SSH'] == 'True'
        self.bitbucket_credentials = None
        if not self.is_bitbucket_ssh:
            self.bitbucket_credentials = {'username': os.environ['BITBUCKET_USERNAME'],
                                          'password': os.environ['BITBUCKET_PASSWORD']}
        self.hound_credentials = (os.environ['HOUND_USERNAME'], os.environ['HOUND_PASSWORD'])
        self.call_name = call_name
        self.client_name = client_name

    def preprocess(self):
        """
        This method runs the preprocessor that creates the dataset for CLAMS by using Hound to filter down to specific files.
        :return:
        """
        for project in projects_map:
            package_name = projects_map[project]['package']

            print "Removing previous session's results..."
            directory = os.path.join(os.getcwd(), 'files', project)
            helper.delete_dir(directory)
            helper.create_dir(directory)
            print "Ready to run new session!\n"

            # search on Hound
            print "\nSearching on Hound..."
            hound_client = HoundClient(self.hound_host, self.hound_credentials)
            hound_query = {'q': 'import ' + package_name, 'i': 'nope', 'files': '.java', 'repos': '*'}
            json_response = hound_client.search(hound_query)
            files_urls = self.parse_hound_response(project, json_response)
            print "Search completed!\n"

            # download files from BitBucket Server
            print "Downloading files..."
            bitbucket_client = BitBucketServerClient(host=self.bitbucket_host, is_ssh=self.is_bitbucket_ssh,
                                                     credentials=self.bitbucket_credentials)
            for file_name, info in files_urls.iteritems():
                response = bitbucket_client.download_file(info)
                helper.write_file_content(response, file_name, directory, self.is_bitbucket_ssh)
            print "Files are now stored locally!\n"

            print 'Writing files\' BitBucket Server urls to file...'
            helper.write_json(files_urls, 'files_urls', directory)
            print 'Files\' BitBucket Server urls are now stored in a json file!\n'
            # sleep for 1s to avoid overloading Hound/BitBucket
            # remove in case you don't have any latency issues
            time.sleep(1)

    def parse_hound_response(self, project, response):
        """
        Receives a response from Hound and parses the content to get files that are good candidates. Also retrieves
        any info needed for the files from response.
        :param project: the project for which search is performed
        :param response: Hound response
        :return: a dictionary where key is the filename and value is a dictionary with any info needed for the file; this
        includes http-path, project, repo and file-path.
        """
        call_pattern = re.compile(self.call_name + ';')
        client_pattern = re.compile(self.client_name)
        files_urls = dict()
        for repo in response['Results']:
            # exclude results from same repo
            if repo != projects_map[project]['repo']:
                proj_results = response['Results'][repo]
                for m in proj_results['Matches']:
                    self.process_repo_matches(repo, m, call_pattern, client_pattern, files_urls)
        return files_urls

    @staticmethod
    def process_repo_matches(repo, m, call_pattern, client_pattern, files_urls):
        """
        Process matches for a repo. That is, it checks whether results should be downloaded and if yes add their info to
        files_urls.
        :param repo: repo to be processed
        :param m: matching result
        :param call_pattern: compiled pattern for regex that call filename should match
        :param client_pattern: compiled pattern for regex that client filename should match
        :param files_urls: a dictionary where key is the filename and value is a dictionary with any info needed for the file; this
        includes http-path, project, repo and file-path.
        :return:
        """
        filename = m['Filename']
        will_download = False
        for l in m['Matches']:
            if re.search(call_pattern, l['Line'].strip()) and re.search(client_pattern, filename):
                will_download = True
                break
        if will_download:
            only_file_name = filename.rsplit('/', 1)[1][:-5]
            project_parts = repo.split('/')
            file_path = project_parts[0] + '/repos/' + project_parts[1] + '/browse/' + filename
            files_urls[only_file_name] = {'http-path': file_path,
                                          'project': project_parts[0],
                                          'repo': project_parts[1],
                                          'file-path': filename
                                          }
        return files_urls
