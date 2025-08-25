from qywx_toolkit import WebhookClient

# 1. 初始化客户端
# webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=aa6f842e-9148-484e-b3b3-ff234357a646"
client = WebhookClient(webhook_url, timeout=5.0)

# 2. 发送文本消息
# try:
#     result = client.send_text(
#         content="今日日志已提交，请审核",
#         mentioned_list=["@all"]
#     )
#     print("文本发送成功：", result)
# except Exception as err:
#     print("文本发送失败：", err)

# 3. 发送 Markdown 消息
payload={
	"msgtype": "markdown_v2",
	"markdown_v2": {
         "content": "# 一、标题\n## 二级标题\n### 三级标题\n# 二、字体\n*斜体*\n\n**加粗**\n# 三、列表 \n- 无序列表 1 \n- 无序列表 2\n  - 无序列表 2.1\n  - 无序列表 2.2\n1. 有序列表 1\n2. 有序列表 2\n# 四、引用\n> 一级引用\n>>二级引用\n>>>三级引用\n# 五、链接\n[这是一个链接](https:work.weixin.qq.com\/api\/doc)\n![](https://res.mail.qq.com/node/ww/wwopenmng/images/independent/doc/test_pic_msg1.png)\n# 六、分割线\n\n---\n# 七、代码\n`这是行内代码`\n```\n这是独立代码块\n```\n\n# 八、表格\n| 姓名 | 文化衫尺寸 | 收货地址 |\n| :----- | :----: | -------: |\n| 张三 | S | 广州 |\n| 李四 | L | 深圳 |\n"
	   }
}
try:
    result = client.send_markdown(payload=payload)
    print("Markdown 发送成功：", result)
except Exception as err:
    print("Markdown 发送失败：", err)
