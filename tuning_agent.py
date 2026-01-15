import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def test_ai_settings(system_prompt, user_prompt, temp_value):
    print(f"\n🧪 测试配置: Temp={temp_value} | 角色={system_prompt}")
    print("-" * 40)
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            # 🌟 今天的重点参数 🌟
            temperature=temp_value, 
            max_tokens=10,
            stream=False
        )
        print(f"🤖 AI 回复:\n{response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ 报错了: {e}")
def test_stream():
    print("测试流式输出:")
    print("-" * 40)
    #1.打开流式输出 stream=True
    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "请写一首关于程序员头发的五言律诗"}],
        stream=True
    )

    print("AI回复:", end="")#end=""表示不换行，等后面字接上来

    #接受方式变了，要用for循环接收"碎片"
    for chunk in stream:
        #获取碎片内容
        content = chunk.choices[0].delta.content
        if content:
            print(content,end="", flush=True)#打印不换行
    
    print("\n")# 最后换行
if __name__ == "__main__":
    test_stream()
    # --- 实验 1: 严谨 vs 疯狂 ---
    prompt = "今天吃什么"
    
    # A组：绝对理性 (Temp = 0)
    test_ai_settings("你是一个只会用emoji表情回答的助手，绝对不要写汉字", prompt, 2.0)
    
    # B组：疯狂创意 (Temp = 1.3 - 注意：DeepSeek最高通常支持到1.5或2.0)
    test_ai_settings("你是一个疯狂的艺术家", prompt, 2.0)