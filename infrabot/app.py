#!/usr/bin/python
import json
import os

import sentry_sdk
import slack
from flask import Flask, request, jsonify
from sentry_sdk.integrations.flask import FlaskIntegration

from release.issuer import ReleaseIssuer
from release.message_builder import ReleaseNotificationBuilder
from utils import slack_response, parse_release

sentry_sdk.init(
    dsn="https://ecbf999a71f748d7b54875ece61195f9@sentry.io/1443099",
    integrations=[FlaskIntegration()],
)

app = Flask(__name__)

slack_client = slack.WebClient(token=os.environ.get("SLACK_TOKEN"))


@app.route("/issue-release", methods=["POST"])
def release():
    args = request.form
    channel = args.get("channel_name")
    if channel == "directmessage":
        return slack_response(
            "Warning", "Please trigger releases from a public slack channel like #dev."
        )
    text = args.get("text")
    project, version, env = parse_release(text)

    if project not in ["clients", "wkpython", "all"]:
        return slack_response(
            "Invalid project: {}".format(project),
            "Must be one of either `clients`, `wkpython`, or `all`.",
        )
    if version != "latest" and not version.startswith("v"):
        return slack_response(
            "Invalid version: {}".format(version),
            "Must be a git version tag or `latest` or empty.",
        )
    if env not in ["prod", "cshs"]:
        return slack_response(
            "Invalid environment: {}".format(project),
            "Must be one of either `prod`, or `cshs`.",
        )
    if project == "all" and version != "latest":
        return slack_response(
            "Invalid version for releasing all projects: {}".format(version),
            "Must be 'latest' or blank.",
        )

    attachments = []
    err, results = ReleaseIssuer(
        channel=channel, project=project, version=version, env=env
    ).make_release()
    if err:
        return err
    for (app, version) in results:
        attachments.append(
            {
                "color": "#149e1d",
                "text": f"Triggered promotion for {app} at version {version}",
            }
        )
    return jsonify(
        {"text": "Success!", "attachments": attachments, "response_type": "in_channel"}
    )


@app.route("/slack-notify", methods=["GET", "POST"])
def notify():
    args = request.args
    challenge = args.get("challenge")
    if challenge != "sixsicksheep":
        return

    is_release = bool(int(args.get("release", 0)))
    if is_release:
        payload = {"blocks": ReleaseNotificationBuilder(**args).get_message_payload()}
    else:
        payload = {"text": args.get("text")}
    resp = slack_client.chat_postMessage(
        channel="#" + args.get("channel", "dev"), **payload
    )
    assert resp["ok"]
    return resp["message"]["text"]


@app.route("/action", methods=["POST"])
def react():
    """
    https://api.slack.com/messaging/interactivity/enabling#understanding_payloads
    {
      "type": "block_actions",
      "team": {
        "id": "T9TK3CUKW",
        "domain": "example"
      },
      "user": {
        "id": "UA8RXUSPL",
        "username": "jtorrance",
        "team_id": "T9TK3CUKW"
      },
      "api_app_id": "AABA1ABCD",
      "token": "9s8d9as89d8as9d8as989",
      "container": {
        "type": "message_attachment",
        "message_ts": "1548261231.000200",
        "attachment_id": 1,
        "channel_id": "CBR2V3XEX",
        "is_ephemeral": false,
        "is_app_unfurl": false
      },
      "trigger_id": "12321423423.333649436676.d8c1bb837935619ccad0f624c448ffb3",
      "channel": {
        "id": "CBR2V3XEX",
        "name": "review-updates"
      },
      "message": {
        "bot_id": "BAH5CA16Z",
        "type": "message",
        "text": "This content can't be displayed.",
        "user": "UAJ2RU415",
        "ts": "1548261231.000200",
        ...
      },
      "response_url": "https://hooks.slack.com/actions/AABA1ABCD/1232321423432/D09sSasdasdAS9091209",
      "actions": [
        {
          "action_id": "WaXA",
          "block_id": "=qXel",
          "text": {
            "type": "plain_text",
            "text": "View",
            "emoji": true
          },
          "value": "click_me_123",
          "type": "button",
          "action_ts": "1548426417.840180"
        }
      ]
    }

    :return:
    :rtype:
    """
    args = request.form
    payload = json.loads(args.get("payload"))
    channel = payload["channel"]["name"]
    user = payload["user"]["username"]
    actions = payload.get("actions", [])
    for action in actions:
        if action.get("action_id") == ReleaseNotificationBuilder.PROMOTE_ACTION_ID:
            btn_value = action["value"]
            project, version = btn_value.split("_")
            err, results = ReleaseIssuer(
                channel=channel, project=project, version=version, env="prod"
            ).make_release()
            if err:
                return err
            slack_client.chat_postMessage(
                channel=channel,
                text=f"@{user} started promotion of `{project}@{version}` to production.",
            )
    return True


@app.route("/")
def root():
    return "Hello."


@app.route("/debug-sentry")
def trigger_error():
    division_by_zero = 1 / 0


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
