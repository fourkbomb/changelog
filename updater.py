#
# Copyright (C) 2017 Simon Shields
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from datetime import datetime

import json
import requests

class Updater:
    def __init__(self, url='https://download.lineageos.org'):
        self.url = url

    def _do_request(path, params=None):
        res = requests.get(self.url + path, params=params)
        return res.json()

    def get(device, romtype='nightly'):
        return [Rom(i) for i in _do_request('/api/v1/%s/%s/abc'%(device, romtype))['response']]


class Rom:
    def __init__(self, obj):
        self.date = datetime.fromtimestamp(obj['date'])
        self.filename = obj['filename']
        self.type = obj['romtype']
        self.version = obj['version']
        self.url = obj['url']
        self.id = obj['id']

