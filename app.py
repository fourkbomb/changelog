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
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template
from gerrit import GerritJSONEncoder, GerritServer, datetime_to_gerrit
from updater import Updater

app = Flask(__name__)
app.config.from_pyfile('app.cfg')
app.json_encoder = GerritJSONEncoder
updater = Updater(app.config['UPDATER_URL'])
gerrit = GerritServer(app.config['GERRIT_URL'])

def get_changes(device=None, before=-1):
    if device is not None:
        last_release = updater.get(device)['date']
    else:
        last_release = datetime.now()-timedelta(days=7)

    # TODO filter out repos that aren't relevant
    is_related_project = lambda p: '/android_' in p or '-kernel-' in p

    # load 50 changes at a time
    query = 'status:merged'
    query += ' after:' + datetime_to_gerrit(last_release)
    if before != -1:
        query += ' before:' + datetime_to_gerrit(datetime.fromtimestamp(before))

    changes = gerrit.changes(query=query, n=50, limit=50)

    nightly_changes = []

    for c in changes:
        if is_related_project(c.project):
            if c.submitted is None:
                # change was probably pushed rather than submitted via gerrit
                # assume updated == submitted
                c.submitted = c.updated
            nightly_changes.append({
                'project': c.project,
                'subject': c.subject,
                'submitted': int(c.submitted.timestamp()),
                'url': c.url,
                'owner': c.owner,
                'labels': c.labels
            })
    return nightly_changes

@app.route('/api/v1/changes/<device>/')
@app.route('/api/v1/changes/<device>/<before>')
def changes(device='all', before=-1):
    if device == 'all':
        device = None
    return jsonify({'res': get_changes(device, before)})

@app.route('/')
def index():
    return render_template('changes.html', device='all')


