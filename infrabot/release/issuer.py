import os

import requests
import subprocess

from utils import slack_response

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

    def _jx_promote(self, app, version):
        cmd = [
            "jx",
            f"promote --app={app} --version={version} --env=production --batch-mode --verbose",
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        o, e = proc.communicate(timeout=60 * 60)

        print("Output: " + o.decode("ascii"))
        print("Error: " + e.decode("ascii"))
        print("code: " + str(proc.returncode))
        return o.decode("ascii")

    def make_release(self):
        results = []
        if self.project in ["wkpython", "all"]:
            err, wkpy_result = get_latest_tag("wkpython", self.version)
            if err:
                return err, wkpy_result
            self._jx_promote(app="wkpython", version=wkpy_result)
            results.append(("wkpython", wkpy_result))

        if self.project in ["clients", "whoknowswebapp", "all"]:
            err, client_result = get_latest_tag("whoknowswebapp", self.version)
            if err:
                return err, client_result
            self._jx_promote(app="whoknowswebapp", version=client_result)
            results.append(("clients", client_result))
        return None, results
