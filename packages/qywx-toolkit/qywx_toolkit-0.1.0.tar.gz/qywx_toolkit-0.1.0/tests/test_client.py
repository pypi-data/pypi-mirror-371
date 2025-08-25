import json
import pytest
import requests

from qywx_toolkit.client import WebhookClient


class DummyResponse:
    """
    模拟 requests.Response 对象
    """
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Error")


def test_send_text_success(monkeypatch):
    captured = {}

    def fake_post(url, headers, data, timeout):
        captured.update({
            "url": url,
            "headers": headers,
            "data": data,
            "timeout": timeout
        })
        return DummyResponse({"errcode": 0, "errmsg": "ok"})

    monkeypatch.setattr(requests, "post", fake_post)

    client = WebhookClient("https://fake-webhook", timeout=3.5)
    result = client.send_text("Hello QYWX", mentioned_list=["@all"])

    # 返回值校验
    assert result == {"errcode": 0, "errmsg": "ok"}

    # 请求参数校验
    assert captured["url"] == "https://fake-webhook"
    assert captured["headers"] == {"Content-Type": "application/json"}
    payload = json.loads(captured["data"])
    assert payload["msgtype"] == "text"
    assert payload["text"]["content"] == "Hello QYWX"
    assert payload["text"]["mentioned_list"] == ["@all"]
    assert captured["timeout"] == 3.5


def test_send_text_http_error(monkeypatch):
    def fake_post(url, headers, data, timeout):
        return DummyResponse({"error": "fail"}, status_code=500)

    monkeypatch.setattr(requests, "post", fake_post)

    client = WebhookClient("https://fake-webhook")
    with pytest.raises(requests.HTTPError):
        client.send_text("This will fail")


def test_send_markdown_success(monkeypatch):
    captured = {}

    def fake_post(url, headers, data, timeout):
        captured.update({
            "url": url,
            "headers": headers,
            "data": data
        })
        return DummyResponse({"errcode": 0, "errmsg": "ok"})

    monkeypatch.setattr(requests, "post", fake_post)

    client = WebhookClient("https://fake-webhook")
    title = "Markdown Title"
    text = "**bold** and _italic_"
    result = client.send_markdown(title, text)

    # 返回值校验
    assert result == {"errcode": 0, "errmsg": "ok"}

    # 请求参数校验
    assert captured["url"] == "https://fake-webhook"
    assert captured["headers"] == {"Content-Type": "application/json"}
    payload = json.loads(captured["data"])
    assert payload["msgtype"] == "markdown"
    assert payload["markdown"]["title"] == title
    assert payload["markdown"]["text"] == text


def test_send_markdown_http_error(monkeypatch):
    def fake_post(url, headers, data, timeout):
        return DummyResponse({"error": "fail"}, status_code=502)

    monkeypatch.setattr(requests, "post", fake_post)

    client = WebhookClient("https://fake-webhook")
    with pytest.raises(requests.HTTPError):
        client.send_markdown("Bad MD", "won't send")
