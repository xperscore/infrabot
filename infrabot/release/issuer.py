import os

import requests

from ..utils import slack_response

JOB_TOKEN = os.environ.get("JOB_TOKEN")
JENKINS_TOKEN = os.environ.get("JENKINS_TOKEN")


def get_latest_tag(remote, version):
    GIT_USER = os.environ.get("GIT_USER")
    GIT_TOKEN = os.environ.get("GIT_TOKEN")

    tags = requests.get(
        "https://api.github.com/repos/xperscore/{remote}/tags".format(remote=remote),
        auth=(GIT_USER, GIT_TOKEN),
    )
    tags = tags.json()
    tags = [tag["name"] for tag in tags if tag["name"].startswith("v")]
    if version == "latest":
        tags.sort(key=lambda s: [int(u) for u in s.strip("v").split(".")], reverse=True)
        version = tags[0]
    if version not in tags:
        return (
            slack_response(
                "Invalid version: {}".format(version), "Tag not found on remote."
            ),
            None,
        )
    return None, version


class ReleaseIssuer(object):
    def __init__(self, *, channel, project, version, env):
        self.channel = channel
        self.project = project
        self.version = version
        self.env = env

    def make_release(self):
        results = []
        if self.project in ["wkpython", "all"]:
            err, wkpy_result = get_latest_tag("wkpython", self.version)
            if err:
                return err, wkpy_result
            resp = requests.post(
                "https://jenkins.jx.b.whoknows.com/job/promote_apps/buildWithParameters",
                auth=("admin", JENKINS_TOKEN),
                params={
                    "token": JOB_TOKEN,
                    "Version": wkpy_result,
                    "notify": self.channel,
                },
                allow_redirects=False,
            )
            resp.raise_for_status()
            results.append(("wkpython", wkpy_result))

        if self.project in ["clients", "all"]:
            err, client_result = get_latest_tag("whoknowswebapp", self.version)
            if err:
                return err, client_result
            resp = requests.post(
                "https://jenkins.jx.b.whoknows.com/job/promote_clients/buildWithParameters",
                auth=("admin", JENKINS_TOKEN),
                params={
                    "token": JOB_TOKEN,
                    "Version": client_result,
                    "notify": self.channel,
                },
                allow_redirects=False,
            )
            resp.raise_for_status()
            results.append(("clients", client_result))
        return None, results
