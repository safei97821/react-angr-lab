from angr_tools import explore_tool, solve_tool

simgr, arg = explore_tool("./crackme")

print("found =", len(simgr.found))

password = solve_tool(simgr, arg)

print("password =", password)

