import os
import json
import requests
import datetime  # <--- 新朋友：用来获取今天日期的
from openai import OpenAI
from dotenv import load_dotenv

# 1. 加载密钥
load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# --- 工具 1：查天气 (和 Day 3 一样) ---
def get_weather(location):
    print(f"⚠️ 正在联网查询 {location} ...")
    try:
        url = f"https://wttr.in/{location}?format=3"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "查询失败"
    except Exception as e:
        return str(e)

# --- 工具 2：写文件 (Day 4 新增核心技能！) ---
def save_to_file(filename, content):
    """
    这个函数负责把内容写入本地文件
    """
    print(f"💾 正在写入文件: {filename}...")
    try:
        # "a" 代表 append (追加模式)，这样不会覆盖旧内容
        # encoding="utf-8" 保证中文不乱码
        with open(filename, "a", encoding="utf-8") as f:
            f.write(content + "\n\n") # 写完换个行
        return f"写入成功！已保存到 {filename}"
    except Exception as e:
        return f"写入失败: {str(e)}"

# --- 工具说明书 (告诉 AI 它现在有两个本事) ---
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取某地的实时天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "城市名(拼音)"}
                },
                "required": ["location"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_to_file",
            "description": "将内容保存到本地文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "文件名，例如 daily_report.md"},
                    "content": {"type": "string", "description": "要写入的具体内容"}
                },
                "required": ["filename", "content"],
            },
        }
    }
]

# --- 主程序 ---
def run_agent():
    # 你的城市
    city = "London" 
    
    # 🌟 这是一个复杂的指令，要求 AI 既要查，又要写
    prompt = f"请查一下 {city} 的天气，根据天气写一条温馨提示，然后把天气和提示都保存到 'weather_diary.md' 文件里。"
    
    print(f"User: {prompt}")
    messages = [{"role": "user", "content": prompt}]

    # 循环对话，因为 AI 可能需要连续调用两次工具 (先查 -> 再写)
    while True:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools_schema,
        )
        ai_msg = response.choices[0].message
        
        # 如果 AI 想要使用工具
        if ai_msg.tool_calls:
            print(f"🤖 Agent 思考: 我需要使用工具...")
            messages.append(ai_msg) # 记账

            for tool_call in ai_msg.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                result = ""
                # 分辨 AI 想用哪个工具
                if func_name == "get_weather":
                    result = get_weather(args.get("location"))
                elif func_name == "save_to_file":
                    result = save_to_file(args.get("filename"), args.get("content"))
                
                print(f"   -> {func_name} 返回: {result}")
                
                # 把工具结果告诉 AI
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        else:
            # 如果 AI 不调用工具了，说明它干完活了
            print("-" * 30)
            print("🏁 AI 最终回复:")
            print(ai_msg.content)
            break

if __name__ == "__main__":
    run_agent()