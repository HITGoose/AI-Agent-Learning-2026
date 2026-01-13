import os
import json
import requests
import datetime
import sys
from openai import OpenAI
from dotenv import load_dotenv

# 1. 初始化
load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# --- 工具箱 (Day 3 & Day 4 的结合) ---

def get_weather(location):
    """联网查天气"""
    print(f"   (🕵️ 正在调用 get_weather 查询 {location}...)")
    try:
        url = f"https://wttr.in/{location}?format=3"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "查询失败"
    except Exception as e:
        return str(e)

def save_to_file(filename, content):
    """把内容写入文件"""
    print(f"   (💾 正在调用 save_to_file 写入 {filename}...)")
    try:
        # 自动补全时间戳，让日记更专业
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        final_content = f"[{timestamp}]\n{content}\n-------------------\n"
        
        with open(filename, "a", encoding="utf-8") as f:
            f.write(final_content)
        return f"写入成功！已追加到 {filename}"
    except Exception as e:
        return f"写入失败: {str(e)}"

# 工具定义
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取城市天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "城市拼音"}
                },
                "required": ["location"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_to_file",
            "description": "保存内容到本地文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "文件名，例如 notes.txt"},
                    "content": {"type": "string", "description": "要保存的内容"}
                },
                "required": ["filename", "content"],
            },
        }
    }
]

# --- 核心交互逻辑 ---
def main():
    print("🤖 AI 助手已启动！(输入 'exit' 或 'quit' 退出)")
    print("您可以问我：'查一下北京的天气' 或 '把刚才的结果保存到文件里'...")
    print("-" * 50)

    # 1. 初始化对话历史 (System Prompt：设定人设)
    messages = [
        {"role": "system", "content": "你是一个乐于助人的 AI 助理。你可以查询天气，也可以帮用户保存笔记。"}
    ]

    # 2. 外层大循环：负责【和用户聊天】
    while True:
        # 获取用户输入
        user_input = input("\nUser: ").strip()
        
        # 退出机制
        if user_input.lower() in ["exit", "quit", "退出"]:
            print("👋 Bye Bye!")
            break
            
        # 把用户的话加入记忆
        messages.append({"role": "user", "content": user_input})

        # 3. 内层逻辑：负责【处理 AI 的回复和工具调用】
        # 这里不需要 while True，因为我们希望 AI 处理完一次就等用户下一次输入
        # 但如果涉及多次工具链（查完再存），DeepSeek 会在一个回合内处理完
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=tools_schema,
            )
            ai_msg = response.choices[0].message
            
            # 如果 AI 只是普通聊天
            if not ai_msg.tool_calls:
                print(f"AI: {ai_msg.content}")
                messages.append(ai_msg) # 存入记忆
                
            # 如果 AI 想用工具
            else:
                messages.append(ai_msg) # 先把 AI "我想用工具" 这句话存进去
                
                # 处理所有工具调用
                for tool_call in ai_msg.tool_calls:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    
                    tool_result = ""
                    if func_name == "get_weather":
                        tool_result = get_weather(args.get("location"))
                    elif func_name == "save_to_file":
                        tool_result = save_to_file(args.get("filename"), args.get("content"))
                    
                    # 把工具结果存入记忆
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })
                
                # 工具跑完了，让 AI 根据结果给用户一个最终回复
                final_response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages
                )
                print(f"AI: {final_response.choices[0].message.content}")
                messages.append(final_response.choices[0].message) # 存入记忆

        except Exception as e:
            print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    main()