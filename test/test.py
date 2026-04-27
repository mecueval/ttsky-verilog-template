import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

def set_inputs(guess=0, verify=0, new_game=0):
    return (guess & 0xF) | (verify << 4) | (new_game << 5)

@cocotb.test()
async def test_guess_game(dut):
    dut._log.info("Start test")

    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    
    dut._log.info("New game")
    dut.ui_in.value = set_inputs(new_game=1)
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = set_inputs(new_game=0)
    await ClockCycles(dut.clk, 2)


    await RisingEdge(dut.clk)  
    secret = int(dut.game_inst.secret_number.value)
    dut._log.info(f"Secret number = {secret}")

    wrong1 = (secret + 1) % 16
    wrong2 = (secret + 2) % 16

    dut._log.info(f"Attempt 1 with guess={wrong1}")
    dut.ui_in.value = set_inputs(guess=wrong1, verify=1)
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = set_inputs(guess=wrong1, verify=0)
    await ClockCycles(dut.clk, 2)

    attempts = (dut.uo_out.value >> 4) & 0x3
    hint = dut.uo_out.value & 0x7
    dut._log.info(f"Attempts left = {attempts}, hint={hint:03b}")
    assert attempts == 2
    assert (hint == 0b010) or (hint == 0b001), "Pista incorrecta"

    dut._log.info(f"Attempt 2 with guess={wrong2}")
    dut.ui_in.value = set_inputs(guess=wrong2, verify=1)
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = set_inputs(guess=wrong2, verify=0)
    await ClockCycles(dut.clk, 2)

    attempts = (dut.uo_out.value >> 4) & 0x3
    hint = dut.uo_out.value & 0x7
    assert attempts == 1
    assert (hint == 0b010) or (hint == 0b001)

    dut._log.info(f"Attempt 3 with guess={secret} (correct)")
    dut.ui_in.value = set_inputs(guess=secret, verify=1)
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = set_inputs(guess=secret, verify=0)
    await ClockCycles(dut.clk, 2)

    correct = (dut.uo_out.value >> 3) & 1
    assert correct == 1
    dut._log.info("Test passed 🎉")