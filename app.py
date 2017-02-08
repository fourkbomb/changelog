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

import json

app = Flask(__name__)
app.config.from_pyfile('app.cfg')
app.json_encoder = GerritJSONEncoder
updater = Updater(app.config['UPDATER_URL'])
gerrit = GerritServer(app.config['GERRIT_URL'])

# device_deps.json is generated using https://github.com/fourkbomb/lineage_dependencies
with open('device_deps.json') as f:
    dependencies = json.load(f)
is_qcom = {}

# TODO check branch
def is_related_change(device, project, branch):
    if not ('/android_' in project or '-kernel-' in project):
        return False

    if device not in dependencies:
        return True

    deps = dependencies[device]
    if project.split('/', maxsplit=1)[1] in deps:
        # device explicitly depends on it
        return True

    if '_kernel_' in project or '_device_' in project or 'samsung' in project or 'nvidia' in project \
            or '_omap' in project or 'FlipFlap' in project:
        return False

    if not ('hardware_qcom_' in project or project.endswith('-caf')):
        # not a qcom-specific HAL
        return True

    # probably a qcom-only HAL
    qcom = True
    if device in is_qcom:
        qcom = is_qcom[device]
    else:
        for dep in deps:
            # Exynos devices either depend on hardware/samsung_slsi* or kernel/samsung/smdk4412
            if 'samsung_slsi' in dep or 'smdk4412' in dep:
                qcom = False
                break
            # Tegras use hardware/nvidia/power
            elif '_nvidia_' in dep:
                qcom = False
                break
            # Omaps use hardware/ti/omap*
            elif '_omap' in dep:
                qcom = False
            # Mediateks use device/cyanogen/mt6xxx-common or kernel/mediatek/*
            elif '_mt6' in dep or '_mediatek_' in dep:
                qcom = False

        is_qcom[device] = qcom

    return qcom

def get_changes(device=None, before=-1):
    last_release = -1
    if device is not None:
        device_info = updater.get(device)
        if len(device_info) > 0:
            last_release = device_info[0]['date']

    # load 50 changes at a time
    query = 'status:merged'
    if last_release != -1:
        query += ' after:' + datetime_to_gerrit(last_release)
    if before != -1:
        query += ' before:' + datetime_to_gerrit(datetime.fromtimestamp(before))

    changes = gerrit.changes(query=query, n=50, limit=50)

    nightly_changes = []

    for c in changes:
        if is_related_change(device, c.project, c.branch):
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

@app.route('/changes/<device>')
@app.route('/')
def index(device='all'):
    return render_template('changes.html', device=device)


