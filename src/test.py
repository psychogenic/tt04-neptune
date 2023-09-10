import math
import cocotb
import os 

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

displayNotes = {
            'NA':     0b00000010, # -
            'A':      0b11101110, # A
            'B':      0b00111110, # b
            'C':      0b10011100, # C
            'D':      0b01111010, # d
            'E':      0b10011110, # E
            'F':      0b10001110, # F
            'G':      0b11110110, # g
            }
            
displayProx = {
            'lowfar':       0b00111000,
            'lowclose':     0b00101010,
            'exact':        0b00000001,
            'hiclose':      0b01000110,
            'hifar':        0b11000100

}

SegmentMask = 0xFF
ProxSegMask = 0xFE

# os.environ['COCOTB_RESOLVE_X'] = 'RANDOM'
async def reset(dut):
    dut.display_single_enable.value = 0
    dut.display_single_select.value = 0
    dut.rst_n.value = 1
    dut.clk_config.value = 1 # 2khz clock
    await ClockCycles(dut.clk, 5)
    dut._log.info("reset")
    dut.input_pulse.value = 1
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.input_pulse.value = 0
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
   
    
async def startup(dut):
    clock = Clock(dut.clk, 500, units="us")
    cocotb.start_soon(clock.start())
    await reset(dut)
    dut.input_pulse.value = 0
            
async def getDisplayValues(dut):
    displayedValues = [None, None]
    attemptCount = 0
    while None in displayedValues or attemptCount < 3:
        displayedValues[int(dut.prox_select.value)] = int(dut.segments.value) << 1
        
        await ClockCycles(dut.clk, 1)
        
        attemptCount += 1
        if attemptCount > 100:
            dut._log.error(f"NEVER HAVE {displayedValues}")
            return displayedValues
            
    # dut._log.info(f'Display Segments: {displayedValues} ( [ {bin(displayedValues[0])} , {bin(displayedValues[1])}])')
    return displayedValues
    
async def inputPulsesFor(dut, tunerInputFreqHz:int, inputTimeSecs=0.51, sysClkHz=1e3):
    numPulses = tunerInputFreqHz * inputTimeSecs 
    pulsePeriod = 1/tunerInputFreqHz
    pulseHalfCycleUs = round(1e6*pulsePeriod/2.0)
    
    displayedValues = [None, None]
        
    for _pidx in range(math.ceil(numPulses)):
        dut.input_pulse.value = 1
        await Timer(pulseHalfCycleUs, units='us')
        dut.input_pulse.value = 0
        await Timer(pulseHalfCycleUs, units='us')
        
    dispV = await getDisplayValues(dut)
    
    return dispV
    


async def setup_tuner(dut):
    dut._log.info("start")
    await startup(dut)
    

async def note_toggle(dut, freq, delta=0, msg="", toggleTime=1.3):
    dut._log.info(msg)
    await startup(dut)
    dispValues = await inputPulsesFor(dut, freq + delta, toggleTime)  
    return dispValues
    
    

async def note_e(dut, eFreq=330, delta=0, msg=""):
    
    dut._log.info(f"E @ {eFreq} delta {delta}")
    dispValues = await note_toggle(dut, freq=eFreq, delta=delta, msg=msg);
    assert dispValues[1] == (displayNotes['E'] & SegmentMask)
    return dispValues


async def note_a(dut, delta=0, msg=""):
    aFreq = 110
    
    dut._log.info(f"A delta {delta}")
    dispValues = await note_toggle(dut, freq=aFreq, delta=delta, msg=msg);
    assert dispValues[1] == (displayNotes['A'] & SegmentMask)
    return dispValues
    
    

async def note_g(dut, delta=0, msg=""):
    gFreq = 196
    
    dut._log.info(f"G delta {delta}")
    dispValues = await note_toggle(dut, freq=gFreq, delta=delta, msg=msg);
    assert dispValues[1] == (displayNotes['G'] & SegmentMask)
    return dispValues
    
    
async def note_b(dut, delta=0, msg=""):
    gFreq = 247
    
    dut._log.info(f"B delta {delta}")
    dispValues = await note_toggle(dut, freq=gFreq, delta=delta, msg=msg, toggleTime=2);
    assert dispValues[1] == (displayNotes['B'] & SegmentMask)
    return dispValues
    
@cocotb.test()
async def note_g_highclose(dut):
    dispValues = await note_g(dut, delta=3, msg="High/close")
    assert dispValues[0] == (displayProx['hiclose'] & ProxSegMask) 
    

 

    
@cocotb.test()
async def note_e_highfar(dut):
    dispValues = await note_e(dut, eFreq=330, delta=20, msg="little E high/far")
    assert dispValues[0] == (displayProx['hifar'] & ProxSegMask) 


    
@cocotb.test()
async def note_fatE_lowfar(dut):
    dispValues = await note_e(dut, eFreq=83, delta=-7, msg="fat E low/far")
    assert dispValues[0] == (displayProx['lowfar'] & ProxSegMask) 
    
    
 
@cocotb.test()
async def note_fatE_exact(dut):
    dispValues = await note_e(dut, eFreq=83, delta=-1, msg="fat E -1Hz")
    assert dispValues[0] == (displayProx['exact'] & ProxSegMask)
    
@cocotb.test()
async def note_e_lowclose(dut):
    dut._log.info("NOTE: delta same as for fat E, but will be close...")
    dispValues = await note_e(dut, eFreq=330, delta=-7, msg="E exact")
    assert dispValues[0] == (displayProx['lowclose'] & ProxSegMask) 


    
@cocotb.test()
async def note_e_exact(dut):
    dispValues = await note_e(dut, eFreq=330, delta=0, msg="E exact")
    assert dispValues[0] == (displayProx['exact'] & ProxSegMask) 

    

@cocotb.test()
async def note_g_lowclose(dut):
    dispValues = await note_g(dut, delta=-4, msg="G low/close")
    assert dispValues[0] == (displayProx['lowclose'] & ProxSegMask) 
   

    
@cocotb.test()
async def note_g_lowfar(dut):
    dispValues = await note_g(dut, delta=-10, msg="G low/far")
    assert dispValues[0] == (displayProx['lowfar'] & ProxSegMask) 
    
     

@cocotb.test()
async def note_a_highfar(dut):
    dispValues = await note_a(dut, delta=7, msg="A high/far")
    assert dispValues[0] == (displayProx['hifar'] & ProxSegMask) 
   



@cocotb.test()
async def note_b_high(dut):
    dispValues = await note_b(dut, delta=4, msg="B high/close")
    assert dispValues[0] == (displayProx['hiclose'] & ProxSegMask) 
 
@cocotb.test()
async def note_a_exact(dut):
    dispValues = await note_a(dut, delta=0, msg="A exact")
    assert dispValues[0] == (displayProx['exact'] & ProxSegMask) 
   


@cocotb.test()
async def note_b_exact(dut):
    dispValues = await note_b(dut, delta=1, msg="B exact")
    assert dispValues[0] == (displayProx['exact'] & ProxSegMask) 
 

   

# don't know how to get this to work yet...
async def FIXMEnote_B_exact(dut):
    dut._log.info("B exact")
    await startup(dut)
    
    
    bFreq = 247
    periodMs = math.ceil(1e3/bFreq)
    noteclock = Clock(dut.input_pulse, periodMs, units="ms")
    cocotb.start_soon(noteclock.start())
    
    await Timer(2000, units='ms')
    dispValues = await getDisplayValues(dut)
    
    assert dispValues[1] == (displayNotes['B'] & SegmentMask)
    assert dispValues[0] == (displayProx['exact'] & ProxSegMask) 
    
    
 
@cocotb.test()
async def success_test(dut):
    await note_toggle(dut, freq=20, delta=0, msg="just toggling -- end");
