import requests
import json


class WebhookClient:
    """
    纯 requests 实现的 Webhook 消息发送客户端
    """

    def __init__(self, webhook_url: str, timeout: float = 5.0):
        self.webhook_url = webhook_url
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json"}

    def send_text(self, content: str, mentioned_list: list[str] | None = None) -> dict:
        payload = {
            "msgtype": "text",
            "text": {
                "content": content,
                "mentioned_list": mentioned_list or []
            }
        }
        resp = requests.post(
            self.webhook_url,
            headers=self.headers,
            data=json.dumps(payload),
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def send_markdown(self, title: str, text: str) -> dict:
        payload = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": text}
        }
        resp = requests.post(
            self.webhook_url,
            headers=self.headers,
            data=json.dumps(payload),
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()
