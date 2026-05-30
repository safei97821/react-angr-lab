from angr_tools import explore_tool, solve_tool

history = []

for i in range(3):

    thought = f"Round {i+1}: 尝试寻找 Success 路径"

    action = "explore_tool"

    simgr, arg = explore_tool("./crackme")

    observation = (
        f"found={len(simgr.found)}, "
        f"active={len(simgr.active)}"
    )

    history.append(
        {
            "thought": thought,
            "action": action,
            "observation": observation
        }
    )

for item in history:

    print("=" * 50)

    print("Thought:")
    print(item["thought"])

    print()

    print("Action:")
    print(item["action"])

    print()

    print("Observation:")
    print(item["observation"])

    print()

password = solve_tool(simgr, arg)

print("=" * 50)
print("Final Result:")
print(password)
