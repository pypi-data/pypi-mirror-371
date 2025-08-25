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

    def send_markdown(self, payload) -> dict:
        """
        :param payload: 要发送的消息。
            开发文档地址：https://developer.work.weixin.qq.com/document/path/99110#markdown%E7%B1%BB%E5%9E%8B
        :return:
        """
        resp = requests.post(
            self.webhook_url,
            headers=self.headers,
            data=json.dumps(payload),
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()
