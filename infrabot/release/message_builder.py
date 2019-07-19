class ReleaseNotificationBuilder:
    PROMOTE_ACTION_ID = "action_promote"
    DIVIDER_BLOCK = [{"type": "divider"}]

    def __init__(self, **job_args):
        self.version = job_args.get("tag")  # TAG_VERSION
        self.repo = job_args.get("repo")  # ORG
        self.job = job_args.get("job")  # BUILD_TAG
        self.job_uri = job_args.get("job_uri")  # RUN_DISPLAY_URL

    def get_message_payload(self):
        return [
            *self._get_title_block(),
            *self._get_changelog_block(),
            *self._get_stats_block(),
            *self._get_action_block(),
            *self._get_hint_block(),
        ]

    def _get_title_block(self):
        text = (
            "A new release has been promoted to <https://staging.whoknows.com|staging>"
        )
        if self.job_uri:
            text = f"{text} by <{self.job_uri}|{self.job or self.job_uri}>"
        return [{"type": "section", "text": {"type": "mrkdwn", "text": text + "."}}]

    def _get_changelog_block(self):
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<https://github.com/xperscore/{self.repo}/releases/tag/v{self.version}| View changelog>",
                },
            }
        ]

    def _get_stats_block(self):
        return [
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Application:*\n{self.repo}"},
                    {"type": "mrkdwn", "text": f"*Version:*\n{self.version}"},
                ],
            }
        ]

    def _get_action_block(self):
        return [
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": ":thumbsup: Promote to Production",
                        },
                        "action_id": self.PROMOTE_ACTION_ID,
                        "value": f"{self.repo}_{self.version}",
                        "confirm": {
                            "title": {"type": "plain_text", "text": "Are you sure?"},
                            "text": {
                                "type": "mrkdwn",
                                "text": f"This action will release version {self.version} of {self.repo} to the production environment.",
                            },
                            "confirm": {"type": "plain_text", "text": "I understand"},
                            "deny": {
                                "type": "plain_text",
                                "text": "No, let's do more QA",
                            },
                        },
                    }
                ],
            }
        ]

    def _get_hint_block(self):
        return [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Promote to other environments with the command `/release {self.repo}@{self.version} to $ENV`",
                    }
                ],
            }
        ]
