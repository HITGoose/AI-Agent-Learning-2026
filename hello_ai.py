import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. 加载你的API钥匙
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

# 检查一下钥匙有没有读取成功 (如果打印None说明没读到)
if not api_key:
    print("❌ 错误：未找到 API Key，请检查 .env 文件！")
else:
    print("✅ API Key 读取成功，正在呼叫 DeepSeek...")

# 2. 建立连接
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# 3. 发送消息
try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个幽默的程序员鼓励师。"},
            {"role": "user", "content": "我刚才配置好了所有环境，准备开始学 AI Agent 了，夸夸我！"}
        ]
    )
    # 4. 打印它的回答
    print("-" * 30)
    print(response.choices[0].message.content)
    print("-" * 30)
except Exception as e:
    print(f"❌ 发生错误：{e}")