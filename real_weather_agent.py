import os
import json
import requests # <--- 新朋友：用来上网的库
from openai import OpenAI
from dotenv import load_dotenv

# 1. 基础设置 (和昨天一样)
load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 2. 定义工具：这次我们玩真的！(True Internet Search)
def get_weather(location):
    print(f"⚠️ 正在请求真实互联网查询 {location} 的天气...")
    
    try:
        # 这里我们使用 wttr.in 这个免费的天气服务
        #1.要去哪里 # format=3 表示返回一种超简洁的文本格式 (例如：Beijing: ☀️ +25°C)
        url = f"https://wttr.in/{location}?format=3"
        
        #2.怎么去 # 发送网络请求 (相当于 Python 替你打开了浏览器)
        response = requests.get(url)
        
        #3.拿到数据了没 # 检查是否成功 (状态码 200 表示网页正常打开)
        if response.status_code == 200:
            weather_data = response.text.strip() # 拿到网页里的文字 #加strip()是为了去掉网页里的空格和换行符
            return weather_data
        else:
            return f"查询失败，网络状态码: {response.status_code}"
            
    except Exception as e:
        return f"发生了错误: {str(e)}"

# 3. 工具说明书 (和昨天一样，不用改)
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取某个城市的当前真实天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市名称，拼音或英文，例如：Beijing, Shanghai",
                    }
                },
                "required": ["location"],
            },
        }
    }
]

# 4. 主程序 (和昨天几乎一样)
def run_agent():
    # ⚠️ 试一个你现在的真实城市！(最好用拼音，因为这个国外天气网对中文支持一般)
    city = "Tongling"  # <--- 在这里改成你所在的城市拼音
    print(f"User: 请帮我查一下 {city} 的天气。")

    messages = [{"role": "user", "content": f"查一下 {city} 的天气"}]

    # 第一次呼叫
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools_schema,
    )

    ai_msg = response.choices[0].message
    
    # 5. 假如 AI 决定要用工具
    if ai_msg.tool_calls:
        tool_call = ai_msg.tool_calls[0]
        # 解析参数
        args = json.loads(tool_call.function.arguments)
        city_name = args.get("location")
        
        # --- 关键时刻：调用真实的函数 ---
        real_result = get_weather(city_name)
        print(f"✅ 真实网络数据返回: {real_result}")
        # ---------------------------

        # 闭环：把查到的真实数据喂给 AI
        messages.append(ai_msg)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": real_result
        })

        # 第二次呼叫：AI 看着真实数据回答你
        final_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        print("-" * 30)
        print("🤖 DeepSeek 看着真实数据说:")
        print(final_response.choices[0].message.content)
        print("-" * 30)

if __name__ == "__main__":
    run_agent()