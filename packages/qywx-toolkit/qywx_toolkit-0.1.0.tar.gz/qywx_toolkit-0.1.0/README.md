# qywx_toolkit

qywx_toolkit 是一个轻量级的纯 `requests` 实现的企业微信机器人 Webhook 客户端，帮助你快速在 Python 项目中发送文本和 Markdown 消息，无需额外依赖。

---

## 特性

- 纯 Python 实现，唯一依赖 `requests`  
- 支持发送文本消息（text）和 Markdown 消息（markdown）  
- 内置 HTTP 状态码检查，调用失败自动抛出异常  
- 简单易用，封装统一的 `WebhookClient` 接口  
- 支持自定义超时时间和 @ 成员提醒列表  

---

## 安装

```bash
pip install qywx_toolkit
