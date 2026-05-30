import angr
import claripy


def explore_tool(binary_path):
    proj = angr.Project(binary_path, auto_load_libs=False)

    check_addr = proj.loader.find_symbol("_check_password").rebased_addr

    arg = claripy.BVS("arg", 8 * 3)

    input_addr = 0x100000

    state = proj.factory.call_state(check_addr, input_addr)

    state.memory.store(input_addr, arg)

    state.solver.add(arg.get_byte(0) == ord("A"))
    state.solver.add(arg.get_byte(1) != ord("B"))
    state.solver.add(arg.get_byte(2) == 0)

    simgr = proj.factory.simulation_manager(state)

    simgr.explore(
        find=lambda s: b"Success!" in s.posix.dumps(1),
        avoid=lambda s: b"Wrong password!" in s.posix.dumps(1)
    )

    return simgr, arg


def solve_tool(simgr, arg):
    if simgr.found:
        found = simgr.found[0]
        solution = found.solver.eval(arg, cast_to=bytes)
        return solution
    return None
