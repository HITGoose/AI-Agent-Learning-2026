import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 1. 加载 .env 里的钥匙
load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 2. 定义一个“假”工具 (Mock Tool)
# 暂时我们不真的去联网查，先假装我们有一个能查天气的函数
# 这样是为了让你理解 Agent 是怎么“思考”去调用工具的
def get_weather(location):
    print(f"⚠️ 正在调用本地函数查询 {location} 的天气...")
    # 这里我们写死一个数据，假装查到了
    if "北京" in location:
        return json.dumps({"location": "Beijing", "temperature": "25", "unit": "celsius", "condition": "Sunny"})
    elif "上海" in location:
        return json.dumps({"location": "Shanghai", "temperature": "22", "unit": "celsius", "condition": "Rainy"})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

# 3. 告诉 AI 它有哪些工具可用 (工具说明书)
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取某个城市的当前天气情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海",
                    }
                },
                "required": ["location"],
            },
        }
    }
]

# 4. 主程序：发送问题给 AI
def run_agent():
    # 用户的问题
    user_query = "上海今天出门需要带伞吗？"
    print(f"User: {user_query}")

    messages = [{"role": "user", "content": user_query}]

    # 第一次呼叫：带上工具说明书
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools_schema,  # 把工具箱递给它
    )

    # 获取 AI 的第一轮回复 (它应该会说：我想调用函数！)
    ai_msg = response.choices[0].message
    
    # 5. 检查 AI 是否想要使用工具
    if ai_msg.tool_calls:
        print("🤖 Agent 思考: 我不知道答案，但我决定使用工具 'get_weather'！")
        
        # 拿到 AI 想要调用的函数名和参数
        tool_call = ai_msg.tool_calls[0]
        function_name = tool_call.function.name
        # 解析参数 (AI 会自动从你的问题里提取出"北京")
        function_args = json.loads(tool_call.function.arguments)
        location_arg = function_args.get("location")

        # 6. 执行函数 (真正的“动手”环节)
        if function_name == "get_weather":
            tool_result = get_weather(location_arg)
            print(f"✅ 工具返回结果: {tool_result}")

            # 7. 把工具查到的结果，回传给 AI (闭环)
            # 我们要把这个结果加到对话历史里，假装是工具告诉它的
            messages.append(ai_msg) # 把 AI 刚才的思考加进去
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })

            # 8. 第二次呼叫：AI 拿到数据后，组织语言回答用户
            final_response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages
            )
            print("-" * 30)
            print("🤖 Agent 最终回复:")
            print(final_response.choices[0].message.content)
            print("-" * 30)
    else:
        print("AI 觉得不需要用工具，直接回答了。")

if __name__ == "__main__":
    run_agent()