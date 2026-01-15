# AI-Agent-Learning-2026
记录一下自学agent的日常
Day 6 成果总结
项目名称: `tuning_agent.py` - API 参数调优与流式输出实验

核心学习内容:
一、API 参数深入理解:
  1.`temperature`: 控制输出随机性，越低随机性越低，反之越高
  2.`max_tokens`: 限制输出长度，ai对话中经常会说一半停止，应该就是这个原因
  3.`stream`: 开启流式输出，实现内容能够一个字一个字流出，而不是片刻停顿后整篇输出，这要求使用for循环配合stream，如不使用则会错误
二、流式输出 (Streaming):
  1.掌握了 `stream=True` 的使用方式
  2.理解了 `chunk.choices[0].delta.content` 与普通响应的区别，delta和message的区别，message是整篇输出
  3.学会了 `flush=True` 的作用（强制实时刷新缓冲区），防止偷懒，缓冲池满了再输出
三、系统提示词 (System Prompt):
  1.通过不同 system prompt 控制 AI 角色（就是cosplay）
  2.理解了 system prompt 对 AI 行为的影响(cosplay不会ooc)

**技术亮点**:
- 掌握了 **流式输出的完整流程**：开启 stream → 循环接收 chunk(碎片) → 实时打印
- 理解了 **API 参数的实际影响**：通过对比实验（不同 temperature）直观感受参数效果
- 学会了 **阅读 API 文档并实践**：从文档到代码的完整学习路径

**代码质量提升**:
- 添加了详细的注释，解释了 `delta`、`flush` 等关键概念
- 代码结构清晰，便于实验和对比不同配置
