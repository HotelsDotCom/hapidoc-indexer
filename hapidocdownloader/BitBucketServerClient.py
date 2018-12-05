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
import subprocess
import sys
import urllib

import requests
import stashy
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import helper

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class BitBucketServerClient:
    """
    Perfoms actions on BitBucket Server (previously known as Stash).
    """

    def __init__(self, host=None, is_ssh=False, credentials=None):
        """
        :param host: BitBucket Server host uri
        """
        self.host = host
        self.is_ssh = is_ssh
        self.credentials = credentials

    def get_bitbucket_server_repos(self, client_repos):
        """
        Retrieves info for the BitBucket Server repos specified.

        :return a list of dictionaries with repos' info
        """
        bitbucket_server_inst = stashy.connect(self.host, self.credentials['username'], self.credentials['password'],
                                               verify=False)

        projects = set()
        project_repos = []
        filtered_repos = set()

        if client_repos == 'all':
            projects = set(bitbucket_server_inst.projects.list())
        else:
            for a in client_repos.split(','):
                spl = a.split('/')
                projects.add(spl[0])
                if len(spl) > 1:
                    filtered_repos.add(a)

        for project in projects:
            project_repos.extend(bitbucket_server_inst.projects[project].repos.list())

        repos = []

        for repo in project_repos:
            try:
                clone_url = (item for item in repo['links']['clone'] if item["name"] == "http").next()
                repo_info = {'project': repo['project']['key'],
                             'slug': repo['slug'],
                             'name': repo['project']['key'] + '-' + repo['slug'],
                             'cloneUrl': clone_url['href'],
                             'browse': repo['links']['self'][0]['href']}

                if not filtered_repos or (repo_info['project'] + '/' + repo_info['slug']) in filtered_repos:
                    repos.append(repo_info)
            except:
                print 'An error occurred when retrieving info for repo: ' + repo['project']['key'] + '/' + repo['slug']
        return repos

    def clone_repo(self, repo, repo_dir):
        """
        Clones the repo passed as an argument into repos_dir directory. Note that this method clones a basic version of
        the repo (depth=1, branch=master)
        :param repo: repository to be cloned
        :param repo_dir: directory where repository will be cloned
        :return:
        """
        project_dir = os.path.join(repo_dir, repo['project'])
        helper.create_dir(project_dir)
        clone_url = repo['cloneUrl'].split('@')[0] + ':' + urllib.quote(self.credentials['password'],
                                                                 safe='') + '@' + \
                    repo['cloneUrl'].split('@')[1]
        command = "git clone --depth 1 -b master %s repos/%s/%s" % (pipes.quote(clone_url), pipes.quote(repo['project']), pipes.quote(repo['slug']))
        os.system(command)

    def download_file(self, info):
        """
        :param info: A dictionary containing all the info needed to download the file (i.e. project, repo, and full
        path of the file)
        :return: the content of the file
        """
        if not self.is_ssh:
            response = self.download_file_http(info['http-path'])
        else:
            response = self.download_file_ssh(info)
        return response

    def download_file_http(self, file_path):
        """
        :param file_path: The full path of the file to be downloaded
        :return: a json object containing the result of the query
        """
        full_address = self.host + '/rest/api/1.0/projects/' + file_path
        response = requests.get(full_address,
                                auth=self.credentials,
                                headers={'content-type': 'application/json', 'accept': 'application/json'},
                                timeout=2)
        if response.status_code is not requests.codes.ok:
            print 'Error - BitBucket server returned code: {}'.format(response.status_code)
            sys.exit(1)
        response_json = response.json()

        return response_json

    def download_file_ssh(self, info):
        """
        :param info: A dictionary containing all the info needed to download the file (i.e. project, repo, and full
        path of the file)
        :return: the content of the file
        """
        remote = self.host + '/rest/api/1.0/projects/' + info['project'] + '/' + info['repo'] + '.git'
        command = 'git archive --remote=' + remote + ' HEAD ' + info['file-path'] + ' | tar -O -xf -'
        process = subprocess.Popen(pipes.quote(command), stdout=subprocess.PIPE, shell=True)
        output = process.communicate()[0]

        return output
