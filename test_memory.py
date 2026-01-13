memory = []
while True:
    input_text = input("请输入：").strip()
    if input_text == "exit":
        break

    memory.append({"role": "user", "content": input_text})

    summary = ""

    for msg in memory:
        if msg['role'] == "user":
          summary += msg['content'] + "|"
    
    fake_ai_response = f"ai say : '{summary}'"
    print(fake_ai_response)
    memory.append({"role": "assistant", "content": fake_ai_response})
    print(f"memory length: {len(memory)}")
    #这些代码是用来模拟AI的记忆能力，AI会记住用户说的话，并根据用户说的话生成回复，方便我学习