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

import json
import os


def create_documents(project, bitbucket_host):
    """
    Creates a list of documents for a given project.
    :param project: the project to be indexed
    :param bitbucket_host: BitBucket Server host
    :return: a list of documents
    """
    calls = set()
    project_path = os.path.join('files', project)
    results_info_file = os.path.join(project_path, 'ranked_files.json')
    files_urls_map = os.path.join(project_path, 'files_urls.json')

    results_info = read_file(results_info_file, is_json=True)
    urls_info = read_file(files_urls_map, is_json=True)

    docs = []
    for idx, result_info in enumerate(results_info):
        try:
            file_info = get_file_info(project_path, int(idx), result_info, urls_info, bitbucket_host)
            docs.append(file_info)
            calls.update(file_info['calls'])
        except IOError:
            print 'Could not retrieve info for file:' + os.path.join(project_path, 'ranked', str(idx) + '.java')

    calls_document = {'type': 'list', 'calls': list(calls)}
    docs.append(calls_document)
    return list(docs)


def get_file_info(project_path, idx, result_info, urls_info, bitbucket_host):
    """
    Stores info needed to be passed in the front-end for each file into a dictionary.
    Info is mainly retrieved by the json files created by the CLAMS system.
    :param project_path: path where results for the project are stored
    :param idx: the id of the file in the list of ranked files
    :param result_info: contains info for the results of the project associated with the file
    :param urls_info: contains the url mapping for the results of the project associated with the file
    :param bitbucket_host: BitBucket host
    :return: a dictionary containing info for the file
    """
    info = dict()
    filename = result_info['name'].split('_')[1]
    method = result_info['name'].split('_')[-1].split('.')[0]
    file_path = os.path.join(project_path, 'ranked', str(idx) + '.java')
    content = read_file(file_path)
    support = result_info['support']
    calls = list(set(result_info['calls']))
    project = urls_info[filename]['project']
    repo = urls_info[filename]['repo']
    info['project'] = project
    info['repo'] = repo
    info['filename'] = filename
    info['content'] = content
    info['bitbucket_server_url'] = bitbucket_host + '/projects/' + urls_info[filename]['http-path']
    info['display_path'] = urls_info[filename]['file-path']
    info['method'] = method
    info['support'] = support
    info['calls'] = calls
    info['type'] = 'result'

    return info


def read_file(file_path, is_json=False):
    """
    Reads the content of a file.
    :param file_path: path of the file
    :param is_json: True if it's a json file
    :return: file's content
    """
    with open(file_path, 'r') as infile:
        if is_json:
            content = json.load(infile)
        else:
            content = infile.read()
    return content
