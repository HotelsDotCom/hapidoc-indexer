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

import errno
import json
import os
import shutil
import sys

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.insert(0, os.path.pardir)


def write_file_content(content, filename, directory, is_ssh=False):
    """
    Get json content and write to java file.
    :type content: dict like
    :param content: the content of the file (in json form if is_ssh is False)
    :type filename: str
    :param filename: the name of the file that will store the data
    :type directory: str
    :param directory: the directory
    :type is_ssh: boolean
    :param is_ssh: True if BitBucket under ssh
    """
    file_path = os.path.join(directory, filename + '.java')
    with open(file_path, 'w') as f:
        if is_ssh:
            f.write(content)
        else:
            for line in content['lines']:
                f.write(line['text'] + os.linesep)


def write_json(content, filename, directory):
    """
    Writes data to json file.
    :type content: dict like
    :param content: the data to be written to file
    :type filename: str
    :param filename: the name of the file that will store the data
    :type directory: str
    :param directory: the directory
    """
    file_path = os.path.join(directory, filename + '.json')
    with open(file_path, 'w') as fp:
        json.dump(content, fp, indent=4)


def delete_dir(directory):
    """
    Deletes a directory if it exists.
    :type directory: str
    :param directory: the directory to be deleted (if it exists)
    """
    if os.path.exists(directory):
        shutil.rmtree(directory)


def create_dir(directory):
    """
    Checks whether a directory exists and creates it in case it is missing.
    :type directory: str
    :param directory: the directory to be created (if it does not exist)
    """
    try:
        os.makedirs(directory)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
