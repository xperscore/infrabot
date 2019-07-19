from flask import jsonify


def slack_response(text, subtext, level=0):
    if level == 1:
        color = "#ff7b00"  # orange
    elif level == 2:
        color = "#149e1d"  # green
    elif level == 3:
        color = "#93bcff"  # blue
    else:
        color = "#d81c1c"  # red

    return jsonify(
        {
            "text": text,
            "attachments": [{"color": color, "text": subtext}],
            "response_type": "in_channel",
        }
    )


def parse_release(text):
    if "@" in text:
        project, rest = text.split("@")
        version, *to_env = rest.split()
        env = to_env[-1]
    else:
        project, *version_to_env = text.split()
        if len(version_to_env) == 0:
            version = "latest"
            env = "prod"
        elif len(version_to_env) == 1:
            version = "latest"
            env = version_to_env[0]
        elif version_to_env[0] == "to":
            version = "latest"
            env = version_to_env[-1]
        else:
            version = version_to_env[0]
            env = version_to_env[-1]

    return project, version, env
