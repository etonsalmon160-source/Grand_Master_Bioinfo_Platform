import requests
import json

def test_pushplus():
    token = "b5300e241cad4d73b36533b5c950e22d"
    title = "🚀 生信分析平台联动成功！"
    content = """
    ## Antigravity x OpenClaw x PushPlus
    
    您的推送通道已经成功打通！
    
    ### 📊 当前状态
    - **通知节点**: 微信推送 (PushPlus)
    - **分析状态**: 自动化监听中
    - **项目**: Grand Master Bioinfo Platform
    
    ✅ 以后每次分析完成后，我都会把核心结论推送到您的手机。
    """
    
    url = "https://www.pushplus.plus/send"
    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": "markdown"
    }
    
    try:
        response = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            print("Successfully sent message to PushPlus!")
            print(response.json())
        else:
            print(f"Failed to send message: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_pushplus()
