import requests
import json

def test_wechat_notification():
    webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=aba93eed94"
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": """# 🚀 Antigravity x OpenClaw 联动成功！\n\n您的**企业微信机器人**已成功接入生信分析平台。\n\n> **当前状态**: 已就绪\n> **控制终端**: OpenClaw Gateway\n\n✅ 以后分析任务完成后，我会在这里为您发送报告摘要。"""
        }
    }
    
    try:
        response = requests.post(webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            print("Successfully sent message to WeChat!")
        else:
            print(f"Failed to send message: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_wechat_notification()
