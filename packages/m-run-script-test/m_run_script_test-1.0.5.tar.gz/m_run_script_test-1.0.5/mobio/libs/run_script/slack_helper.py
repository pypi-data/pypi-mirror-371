import os
import datetime
import requests


class SlackHelper:
    def __init__(self, slack_uri=None):
        self.slack_uri = slack_uri if slack_uri else os.environ.get("SLACK_URI_RESTART_POD")

    def send_alert(self, content, title=None, author_name=None, pretext=None, success=True):
        result = {}
        if self.slack_uri:
            try:
                color = "#15d60b" if success else "#dc3907"
                data_json = {
                    "attachments": [
                        {
                            "color": color,
                            "pretext": pretext if pretext else "",
                            "title": title if title else "",
                            "author_name": author_name if author_name else "",
                            "text": content,
                            "fields": [
                                {
                                    "title": "Date",
                                    "value": str(datetime.datetime.now(datetime.UTC)),
                                    "short": True,
                                },
                                {"title": "VM", "value": os.getenv('VM_TYPE', None), "short": True},
                            ],
                        }
                    ]
                }
                response = requests.post(self.slack_uri, json=data_json, timeout=30)
                result.update({
                    "code": response.status_code,
                    "text": response.text,
                })
            except Exception as ex:
                print("send_alert err: {}".format(ex))
                result.update({
                    "text": str(ex),
                })
        else:
            print("slack_uri not exists")
        print("send_alert result: {}".format(result))
        return result


if __name__ == '__main__':
    slack_test = "https://hooks.slack.com/services/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"
    alert_result = SlackHelper(slack_test).send_alert()

