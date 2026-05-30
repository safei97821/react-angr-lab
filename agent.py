import json
from openai import OpenAI
from angr_tools import explore_tool, solve_tool

client = OpenAI(
    api_key="sk-58cf7d445ae243968fa92e928742a4d2",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

simgr_cache = None
arg_cache = None

tools = [
    {
        "type": "function",
        "function": {
            "name": "explore_tool",
            "description": "Use angr to explore crackme and find the Success path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "binary_path": {
                        "type": "string",
                        "description": "Path to the binary file"
                    }
                },
                "required": ["binary_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "solve_tool",
            "description": "Solve symbolic input after explore_tool finds a success state.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


messages = [
    {
        "role": "system",
        "content": """
你是一个 ReAct 逆向分析智能体。
你需要通过 Thought -> Action -> Observation 的方式解决 crackme 密码问题。
你不能直接猜密码，必须调用工具完成分析。
"""
    },
    {
        "role": "user",
        "content": "请分析 ./crackme，找到能够进入 Success 路径并避开 dead loop/trap 的输入。"
    }
]


def run_tool(name, args):
    global simgr_cache, arg_cache

    if name == "explore_tool":
        binary_path = args.get("binary_path", "./crackme")
        simgr_cache, arg_cache = explore_tool(binary_path)

        return {
            "tool": "explore_tool",
            "found": len(simgr_cache.found),
            "active": len(simgr_cache.active),
            "deadended": len(simgr_cache.deadended),
            "observation": "angr exploration finished"
        }

    if name == "solve_tool":
        if simgr_cache is None or arg_cache is None:
            return {
                "error": "Please call explore_tool first."
            }

        password = solve_tool(simgr_cache, arg_cache)

        return {
            "tool": "solve_tool",
            "password_bytes": repr(password),
            "password_text": password.replace(b"\x00", b"").decode("utf-8", errors="ignore")
        }

    return {
        "error": "Unknown tool"
    }


for i in range(5):
    response = client.chat.completions.create(
        model="qwen-plus",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    msg = response.choices[0].message
    messages.append(msg)

    print("=" * 60)
    print(f"LLM Round {i + 1}")

    if msg.content:
        print(msg.content)

    if msg.tool_calls:
        for tool_call in msg.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments or "{}")

            print("Action:")
            print(tool_name)
            print("Action Input:")
            print(tool_args)

            observation = run_tool(tool_name, tool_args)

            print("Observation:")
            print(observation)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(observation, ensure_ascii=False)
                }
            )
    else:
        break