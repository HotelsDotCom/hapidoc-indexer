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
import pipes
import re
import sys
from shutil import copyfile

sys.path.insert(0, os.path.pardir)

from BitBucketServerClient import BitBucketServerClient
from mappings import projects_map
import helper


class NaivePreprocessor:
    """
    This preprocessor creates the dataset for CLAMS by cloning all repos and filtering locally.
    """

    def __init__(self, client_repos, client_name):
        """
        Instantiates a NaivePreprocessor, and sets local variables based on environment ones.
        :param client_name: regex that client filename should match
        """
        self.bitbucket_host = os.environ['BITBUCKET_HOST']
        self.bitbucket_credentials = {'username': os.environ['BITBUCKET_USERNAME'],
                                      'password': os.environ['BITBUCKET_PASSWORD']}
        self.client_name = client_name
        self.client_repos = client_repos

    def preprocess(self):
        """
        Naive preprocessor that creates the dataset for CLAMS by cloning all repos and filtering locally.
        :return:
        """
        repos_dir = os.path.join(os.getcwd(), 'repos')
        helper.create_dir(repos_dir)

        bitbucket_client = BitBucketServerClient(host=self.bitbucket_host, is_ssh=False,
                                                 credentials=self.bitbucket_credentials)
        repos = bitbucket_client.get_bitbucket_server_repos(self.client_repos)
        self.clone_repos(bitbucket_client, repos, repos_dir)

        for project in projects_map:
            package_name = projects_map[project]['package']

            print "Removing previous session's results..."
            directory = os.path.join(os.getcwd(), 'files', project)
            helper.delete_dir(directory)
            helper.create_dir(directory)
            print "Ready to run new session!\n"

            # use the following command to filter files
            os.system(
                "find ./repos -iname '*.java' | xargs -n16 -P8 grep -l" + " \"" + package_name + "\" > " + project +
                ".txt")

            fname = project + ".txt"
            files_urls = {}
            if os.path.exists(fname):
                self.process_filtered_results(directory, files_urls, fname, project)

                print 'Writing files\' BitBucket Server urls to file...'
                helper.write_json(files_urls, 'files_urls', directory)
                print 'Files\' BitBucket urls are now stored in a json file!\n'
            else:
                print 'No usage examples found for ' + project

    def process_filtered_results(self, directory, files_urls, fname, project):
        """
        Processes filtered results. That is, it adds their info (e.g. project and repo name) to files_urls and copies
        them to the directory where results will be stored.
        :param directory: directory where results are stored
        :param files_urls: a dictionary where key is the filename and value is a dictionary with any info needed for the
        file; this includes http-path, project, repo and file-path.
        :param fname: temporary file where filtering results are stored
        :param project: project that's currently being processed
        :return:
        """
        with open(fname) as f:
            for full_file_path in f.readlines():
                full_file_path = full_file_path.strip()
                res_project, res_repo, res_file_path, res_file_name, res_http_path = self.extract_file_info(
                    full_file_path)
                if self.keep_file(project, res_repo, res_file_path):
                    files_urls[res_file_name] = {'http-path': res_http_path, 'project': res_project,
                                                 'repo': res_repo, 'file-path': res_file_path}
                    copied_file_path = os.path.join(directory, res_file_name + '.java')
                    copyfile(pipes.quote(full_file_path), pipes.quote(copied_file_path))

    def keep_file(self, project, res_repo, full_file_path):
        """
        Decides on whether to download the file or not based on the client name regex.
        :param project: the name of the project for which snippets are being mined
        :param res_repo: the name of the -client- repository that's being processed
        :param full_file_path: the full file path of the file in question
        :return:
        """
        if project != res_repo and re.search(self.client_name, full_file_path):
            return True
        else:
            return False

    @staticmethod
    def clone_repos(bitbucket_client, repos, repos_dir):
        """
        Clones the repos in the list.
        :param bitbucket_client: BitBucketServerClient instance
        :param repos: list of repositories to be cloned
        :param repos_dir: directory where repositories will be cloned
        :return:
        """
        for repo in repos:
            bitbucket_client.clone_repo(repo, repos_dir)

    @staticmethod
    def extract_file_info(full_file_path):
        pattern = re.compile(r"""\./repos              # current dir
                                 /(?P<project>.*?)     # project name
                                 /(?P<repo>.*?)        # slash, repo name
                                 /(?P<filepath>.*$)    # slash, filepath
                                 """, re.VERBOSE)

        match = pattern.match(full_file_path)

        project = match.group("project")
        repo = match.group("repo")
        file_path = match.group("filepath")

        file_name = file_path.rsplit('/', 1)[1][:-5]
        http_path = project + '/repos/' + repo + '/browse/' + file_path

        return project, repo, file_path, file_name, http_path
