"""
Temporal + Spatial Summation Demo using NetPyNE

Neuron A:
- Receives temporally close excitatory inputs (AMPA)
- Temporal summation drives it above threshold
- Fires an action potential

Neuron B:
- Receives inhibitory synapse (GABA_A-like) from Neuron A
- Shows spatial integration of inhibition

Live animation visualizes:
- Voltage of Neuron A (spiking)
- Voltage of Neuron B (hyperpolarization)
"""

# =============================================================================
# Imports
# =============================================================================
from netpyne import specs, sim
import matplotlib
matplotlib.use('TkAgg')  # Reliable interactive backend (Windows/Linux)
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# =============================================================================
# Network parameters
# =============================================================================
netParams = specs.NetParams()

# ----------------------------------------------------------------------------
# Cell models
# ----------------------------------------------------------------------------
# Spiking neuron (Neuron A)
netParams.cellParams['spiking_cell'] = {
    'secs': {
        'soma': {
            'geom': {'L': 20, 'diam': 20, 'cm': 1},
            'mechs': {
                'hh': {},
                'pas': {'g': 0.00003, 'e': -70}
            },
            'vinit': -70
        }
    }
}

# Passive neuron (Neuron B)
netParams.cellParams['passive_cell'] = {
    'secs': {
        'soma': {
            'geom': {'L': 20, 'diam': 20, 'cm': 1},
            'mechs': {
                'pas': {'g': 0.00003, 'e': -70}
            },
            'vinit': -70
        }
    }
}

# ----------------------------------------------------------------------------
# Populations
# ----------------------------------------------------------------------------
netParams.popParams['PopA'] = {'cellType': 'spiking_cell', 'numCells': 1}
netParams.popParams['PopB'] = {'cellType': 'passive_cell', 'numCells': 1}

# ----------------------------------------------------------------------------
# Synaptic mechanisms
# ----------------------------------------------------------------------------
# Excitatory AMPA
netParams.synMechParams['AMPA'] = {
    'mod': 'Exp2Syn',
    'tau1': 0.5,
    'tau2': 5.0,
    'e': 0
}

# Inhibitory GABA
netParams.synMechParams['GABA'] = {
    'mod': 'Exp2Syn',
    'tau1': 0.5,
    'tau2': 10.0,
    'e': -80
}

# ----------------------------------------------------------------------------
# Temporal summation input to Neuron A
# ----------------------------------------------------------------------------
netParams.stimSourceParams['excStimA'] = {
    'type': 'NetStim',
    'start': 20,
    'interval': 4,   # close spikes for temporal summation
    'number': 3,
    'noise': 0
}

netParams.stimTargetParams['excStimA->A'] = {
    'source': 'excStimA',
    'conds': {'pop': 'PopA'},
    'synMech': 'AMPA',
    'weight': 0.002,
    'delay': 1,
    'sec': 'soma',
    'loc': 0.5
}

# ----------------------------------------------------------------------------
# Inhibitory connection: Neuron A -> Neuron B
# ----------------------------------------------------------------------------
netParams.connParams['A->B_inhibition'] = {
    'preConds': {'pop': 'PopA'},
    'postConds': {'pop': 'PopB'},
    'synMech': 'GABA',
    'weight': 0.003,
    'delay': 2,
    'sec': 'soma',
    'loc': 0.5
}

# =============================================================================
# Simulation configuration
# =============================================================================
simConfig = specs.SimConfig()

simConfig.duration = 120
simConfig.dt = 0.025
simConfig.recordStep = 0.025
simConfig.verbose = False

simConfig.recordCells = [0, 1]
simConfig.recordTraces = {
    'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}
}

# =============================================================================
# Run simulation
# =============================================================================
print("Running simulation...")
sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)
print("Simulation finished.")

# =============================================================================
# Extract recorded data
# =============================================================================
time = sim.allSimData['t']
V_A = sim.allSimData['V_soma']['cell_0']
V_B = sim.allSimData['V_soma']['cell_1']

# =============================================================================
# Live animation
# =============================================================================
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_xlim(0, simConfig.duration)
ax.set_ylim(-90, 40)
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Membrane potential (mV)')
ax.set_title('Temporal Summation → Spike → Inhibitory Spatial Effect')
ax.grid(alpha=0.3)

line_A, = ax.plot([], [], 'r', lw=2, label='Neuron A (spiking)')
line_B, = ax.plot([], [], 'b', lw=2, label='Neuron B (inhibited)')
ax.legend(loc='upper right')


def init():
    line_A.set_data([], [])
    line_B.set_data([], [])
    return line_A, line_B


def update(frame):
    step = 10
    idx = min(frame * step, len(time))
    line_A.set_data(time[:idx], V_A[:idx])
    line_B.set_data(time[:idx], V_B[:idx])
    return line_A, line_B

frames = len(time) // 10
ani = FuncAnimation(fig, update, frames=frames, init_func=init,
                    interval=60, blit=False, repeat=True)

print("Starting live animation...")
plt.show()

# =============================================================================
# Summary
# =============================================================================
print("\nRESULT SUMMARY")
print("------------------------------")
print(f"Neuron A peak voltage: {max(V_A):.2f} mV")
print(f"Neuron B minimum voltage: {min(V_B):.2f} mV")
print("\nInterpretation:")
print("- Neuron A integrates temporally close EPSPs and fires an action potential.")
print("- That spike triggers inhibitory synaptic input onto Neuron B.")
print("- Neuron B hyperpolarizes, demonstrating spatial summation of inhibition.")