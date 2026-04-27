import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

def set_inputs(dut, guess=0, verify=0, new_game=0):
    dut.ui_in.value = (guess & 0xF) | (verify << 4) | (new_game << 5)

@cocotb.test()
async def test_guess_game(dut):
    clock = Clock(dut.clk, 2, unit="us")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # Nuevo juego
    set_inputs(dut, new_game=1)
    await ClockCycles(dut.clk, 1)
    set_inputs(dut, new_game=0)
    await ClockCycles(dut.clk, 2)

    # Intento 1
    set_inputs(dut, guess=3, verify=1)
    await ClockCycles(dut.clk, 1)
    set_inputs(dut, guess=3, verify=0)
    await ClockCycles(dut.clk, 2)

    uo = dut.uo_out.value.integer
    attempts = (uo >> 4) & 0x3
    hint = uo & 0x7

    assert attempts == 2
    assert hint in [0b001, 0b010] 

    # Intento 2
    set_inputs(dut, guess=7, verify=1)
    await ClockCycles(dut.clk, 1)
    set_inputs(dut, guess=7, verify=0)
    await ClockCycles(dut.clk, 2)

    uo = dut.uo_out.value.integer
    attempts = (uo >> 4) & 0x3

    assert attempts == 1

    dut._log.info("Test passed 🎉")