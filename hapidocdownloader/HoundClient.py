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

import requests
import sys


class HoundClient:
    """
    Perfoms actions on Hound.
    """

    def __init__(self, host, credentials):
        """
        :param host: Hound host uri
        :param credentials Hound credentials
        """
        self.host = host
        self.credentials = credentials

    def search(self, query, timeout=3):
        """
        Perfoms a search on Hound.
        :param query: The query in a dictionary in the form {'q': <query>, 'i': <ignore_case>, 'files': <files_regex>,
        'repos': <repos_list>}
        :param timeout: timeout to avoid overloading the server
        :return: a json object containing the result of the query
        """
        response = requests.get(self.host + '/api/v1/search',
                                params=query,
                                headers={'content-type': 'application/json', 'accept': 'application/json'},
                                auth=self.credentials,
                                verify=False,
                                timeout=timeout)
        if response.status_code is not requests.codes.ok:
            print 'Error - Hound server returned code: {}'.format(response.status_code)
            sys.exit(1)
        response_json = response.json()

        return response_json
