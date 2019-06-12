#!/usr/bin/python

import os

import requests
import sentry_sdk
from flask import Flask, jsonify, request
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://ecbf999a71f748d7b54875ece61195f9@sentry.io/1443099",
    integrations=[FlaskIntegration()]
)

app = Flask(__name__)


def slack_response(text, subtext, level=0):
    if level == 1:
        color = "#ff7b00"  # orange
    elif level == 2:
        color = "#149e1d"  # green
    else:
        color = "#d81c1c"  # red

    return jsonify({
        "text": text,
        "attachments": [
            {
                "color": color,
                "text": subtext
            }
        ],
        "response_type": "in_channel"
    })


def get_latest_tag(remote, version):
    GIT_USER = os.environ.get("GIT_USER")
    GIT_TOKEN = os.environ.get("GIT_TOKEN")

    tags = requests.get("https://api.github.com/repos/xperscore/{remote}/tags".format(remote=remote),
                        auth=(GIT_USER, GIT_TOKEN))
    tags = tags.json()
    tags = [tag["name"] for tag in tags if tag["name"].startswith("v")]
    if version == "latest":
        tags.sort(key=lambda s: [int(u) for u in s.strip("v").split('.')], reverse=True)
        version = tags[0]
    if version not in tags:
        return True, slack_response("Invalid version: {}".format(version), "Tag not found on remote.")
    return False, version


@app.route('/issue-release', methods=['POST'])
def release():
    JOB_TOKEN = os.environ.get("JOB_TOKEN")
    JENKINS_TOKEN = os.environ.get("JENKINS_TOKEN")

    args = request.form
    channel = args.get("channel_name")
    if channel == "directmessage":
        return slack_response("Warning", "Please trigger releases from a public slack channel like #dev.")

    text = args.get("text")
    project, *version = text.split()

    if len(version) == 0:
        version = 'latest'
    else:
        version = version[0]
    if project not in ["clients", "wkpython", "all"]:
        return slack_response("Invalid project: {}".format(project),
                              "Must be one of either 'clients', 'wkpython', or 'all'.")
    if version != "latest" and not version.startswith("v"):
        return slack_response("Invalid version: {}".format(version), "Must be a git version tag or 'latest' or blank.")

    if project == "all" and version != "latest":
        return slack_response("Invalid version for releasing all projects: {}".format(version),
                              "Must be 'latest' or blank.")

    attachments = []
    if project in ["wkpython", "all"]:
        err, wkpy_result = get_latest_tag("wkpython", version)
        if err:
            return wkpy_result
        resp = requests.post("https://jenkins.jx.b.whoknows.com/job/promote_apps/buildWithParameters",
                             auth=('admin', JENKINS_TOKEN),
                             params={'token': JOB_TOKEN, "Version": wkpy_result, "notify": channel},
                             allow_redirects=False)
        resp.raise_for_status()
        attachments.append({
            "color": "#149e1d",
            "text": "Triggered promotion for wkpython at version {0}".format(wkpy_result)
        })

    if project in ["clients", "all"]:
        err, client_result = get_latest_tag("whoknowswebapp", version)
        if err:
            return client_result
        resp = requests.post("https://jenkins.jx.b.whoknows.com/job/promote_clients/buildWithParameters",
                             auth=('admin', JENKINS_TOKEN),
                             params={'token': JOB_TOKEN, "Version": client_result, "notify": channel},
                             allow_redirects=False)
        resp.raise_for_status()
        attachments.append({
            "color": "#149e1d",
            "text": "Triggered promotion for clients at version {0}".format(client_result)
        })
    return jsonify({
        "text": "Success!",
        "attachments": attachments,
        "response_type": "in_channel"
    })


@app.route('/slack-notify', methods=['GET', 'POST'])
def notify():
    args = request.args
    challenge = args.get('challenge')
    if challenge != 'sixsicksheep':
        return

    SLACK_TOKEN = os.environ.get("SLACK_TOKEN")

    level = int(args.get('level', 2))

    if level == 1:
        color = "#ff7b00"  # orange
    elif level == 2:
        color = "#149e1d"  # green
    elif level == 3:
        color = "#93bcff"  # blue
    else:
        color = "#d81c1c"  # red

    message = {
        "text": "Job Status",
        "channel": "#" + args.get('channel', 'dev'),
        "attachments": [{
            "author_name": args.get("job", "Jenkins Pipeline"),
            "color": color,
            "text": args.get('text')
        }]
    }
    headers = {"Authorization": "Bearer {token}".format(token=SLACK_TOKEN)}
    resp = requests.post("https://slack.com/api/chat.postMessage", headers=headers, json=message)
    resp.raise_for_status()
    return resp.text


@app.route('/')
def root():
    return "Hello."


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
