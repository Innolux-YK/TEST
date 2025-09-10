from autogen import AssistantAgent

# === 定義專職 Agents ===
stock_agent = AssistantAgent(
    name="StockAgent",
    system_message="你是一個股票分析專家，負責處理所有跟股票投資、選股有關的任務。"
)

docqa_agent = AssistantAgent(
    name="DocQAAgent",
    system_message="你是一個文件問答專家，負責處理所有 PDF、文件、檔案的分析與 QA 任務。"
)

monitor_agent = AssistantAgent(
    name="MonitorAgent",
    system_message="你是一個系統監控專家，負責處理 CPU/GPU 使用率、溫度、效能監控相關的任務。"
)

# === 所有 Agents ===
all_agents = [stock_agent, docqa_agent, monitor_agent]

# === 自動生成 RouterAgent 的 system_message ===
available_agents = "\n".join(
    [f"- {a.name}: {a.system_message}" for a in all_agents]
)

router_system_message = f"""
你是一個任務路由器，負責將任務指派給合適的 Agent。
以下是可用的 Agent 名單與描述：
{available_agents}

請根據使用者輸入判斷最合適的 Agent，並且只輸出 Agent 名稱。
"""

router_agent = AssistantAgent(
    name="RouterAgent",
    system_message=router_system_message
)

# === 定義混合 Router ===
def hybrid_router(task: str):
    if "股票" in task or "投資" in task:
        return "StockAgent"
    elif "PDF" in task or "文件" in task or "檔案" in task:
        return "DocQAAgent"
    elif "監控" in task or "CPU" in task or "GPU" in task:
        return "MonitorAgent"

    decision = router_agent.generate_reply(messages=[{"role":"user", "content": task}])
    return decision.strip()

# === 功能查詢 (自然語言) ===
def capability_query(task: str):
    capability_agent = AssistantAgent(
        name="CapabilityAgent",
        system_message=f"""
        你是一個說明專家，負責根據使用者問題判斷有哪些 Agent 可以處理。
        以下是目前可用的 Agent：
        {available_agents}

        如果使用者問「你會什麼」「有什麼功能」，請列出全部 Agents 和說明。
        如果使用者問「能不能處理某種任務」，請回答「可以，請使用 XXXAgent」或「抱歉，目前沒有 Agent 能處理這個任務」。
        """
    )
    reply = capability_agent.generate_reply(messages=[{"role": "user", "content": task}])
    return reply

# === 任務入口 ===
def task_manager(task: str):
    print(f"\n📥 任務輸入: {task}")

    # 功能查詢模式
    if any(keyword in task for keyword in ["你會什麼", "功能", "能不能", "會不會", "可以處理"]):
        reply = capability_query(task)
        print(f"💡 功能查詢回覆: {reply}")
        return reply

    # 正常任務模式
    agent_name = hybrid_router(task)
    print(f"👉 指派給: {agent_name}")

    target_agent = next((a for a in all_agents if a.name == agent_name), None)

    if target_agent:
        reply = target_agent.generate_reply(messages=[{"role":"user", "content": task}])
    else:
        reply = f"⚠️ 無法找到合適的 Agent ({agent_name})"

    print(f"✅ 輸出: {reply}")
    return reply

# === 測試 ===
task_manager("你會什麼")
task_manager("你能幫我處理 PDF 嗎？")
task_manager("你會不會看股票？")
task_manager("能不能監控 CPU 溫度？")
task_manager("幫我檢查一下財務狀況")  # 走 Router 分派
