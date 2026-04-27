import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

def set_inputs(dut, guess=0, verify=0, new_game=0):
    """Configura las entradas del DUT (ui_in)"""
    dut.ui_in.value = (guess & 0xF) | (verify << 4) | (new_game << 5)

async def get_uo_safe(dut, max_cycles=20):
    """
    Lee uo_out esperando a que no tenga valores X/Z.
    Retorna el valor como entero (0-255).
    """
    for _ in range(max_cycles):
        val = dut.uo_out.value
        if val.is_resolvable:
         
            return val.to_unsigned()
        await ClockCycles(dut.clk, 1)
    raise Exception(f"uo_out no se estabilizó después de {max_cycles} ciclos")

@cocotb.test()
async def test_guess_game(dut):
    dut._log.info("Start test")

    # Reloj de 2 us (500 kHz)
    clock = Clock(dut.clk, 2, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)  
    dut._log.info("New game")
    set_inputs(dut, new_game=1)
    await ClockCycles(dut.clk, 1)
    set_inputs(dut, new_game=0)
    await ClockCycles(dut.clk, 3)

    dut._log.info("Attempt 1: guess=3")
    set_inputs(dut, guess=3, verify=1)
    await ClockCycles(dut.clk, 1)
    set_inputs(dut, guess=3, verify=0)
    await ClockCycles(dut.clk, 3)   

    uo = await get_uo_safe(dut)

    attempts = (uo >> 4) & 0x3
    hint = uo & 0x7

    dut._log.info(f"Attempt1 -> attempts={attempts}, hint={hint:03b}")

    assert attempts == 2, f"Se esperaban 2 intentos restantes, se obtuvo {attempts}"
    assert hint in (0b001, 0b010), f"Hint debe ser 001 (higher) o 010 (lower), se obtuvo {hint:03b}"


    dut._log.info("Attempt 2: guess=7")
    set_inputs(dut, guess=7, verify=1)
    await ClockCycles(dut.clk, 1)
    set_inputs(dut, guess=7, verify=0)
    await ClockCycles(dut.clk, 3)

    uo = await get_uo_safe(dut)

    attempts = (uo >> 4) & 0x3

    dut._log.info(f"Attempt2 -> attempts={attempts}")

    assert attempts == 1, f"Se esperaba 1 intento restante, se obtuvo {attempts}"


    dut._log.info("Test passed ")