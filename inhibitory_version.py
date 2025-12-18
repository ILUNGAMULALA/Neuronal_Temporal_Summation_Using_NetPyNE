"""
Temporal Summation Experiment using NetPyNE (Inhibitory Version)

This script now demonstrates temporal summation of inhibitory postsynaptic potentials (IPSPs):
1. Wide spike interval (20.0, 60.0 ms) - minimal summation
2. Narrow spike interval (20.0, 25.0 ms) - clear temporal summation of inhibition

Key changes for inhibition:
- Synapse renamed to 'GABA' (for clarity)
- Reversal potential 'e' set to -80 mV (below resting potential → hyperpolarizing IPSPs)
- Decay time constant tau2 increased to 10 ms (typical for GABA_A synapses)
- Weight remains positive 0.001 (magnitude of conductance; sign determined by reversal potential)
- Y-axis limits adjusted to show hyperpolarization
- Title and legend updated to reflect inhibition
"""

# Import necessary modules
from netpyne import specs, sim
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib

matplotlib.use('TkAgg')  # Ensures interactive window stays open

# Network Parameters (netParams)
netParams = specs.NetParams()

# Cell Properties (passive single-compartment)
netParams.cellParams['passive_cell'] = {
    'secs': {
        'soma': {
            'geom': {'diam': 18.8, 'L': 18.8, 'Ra': 123.0, 'cm': 1.0},
            'mechs': {'pas': {'g': 0.0000357, 'e': -70}},
            'vinit': -70
        }
    }
}

# Population
netParams.popParams['postPop'] = {
    'cellType': 'passive_cell',
    'numCells': 2
}

# Synapse Mechanisms (Now Inhibitory GABA_A-like)
netParams.synMechParams['GABA'] = {
    'mod': 'Exp2Syn',
    'tau1': 0.5,    # Rise time (ms)
    'tau2': 10.0,   # Decay time (ms) - it is longer for GABA
    'e': -80        # Reversal potential (mV) - KEY PARAMETER FOR INHIBITION
}

# Stimulation Sources
netParams.stimSourceParams['stimWide'] = {
    'type': 'NetStim', 'start': 20.0, 'interval': 40.0, 'noise': 0, 'number': 2
}
netParams.stimTargetParams['stimWide->post0'] = {
    'source': 'stimWide',
    'conds': {'pop': 'postPop', 'cellList': [0]},
    'synMech': 'GABA',      # Use inhibitory synapse
    'weight': 0.001,        # Positive weight (magnitude); no change needed
    'delay': 1.0,
    'sec': 'soma',
    'loc': 0.5
}

netParams.stimSourceParams['stimNarrow'] = {
    'type': 'NetStim', 'start': 20.0, 'interval': 5.0, 'noise': 0, 'number': 2
}
netParams.stimTargetParams['stimNarrow->post1'] = {
    'source': 'stimNarrow',
    'conds': {'pop': 'postPop', 'cellList': [1]},
    'synMech': 'GABA',      # Use inhibitory synapse
    'weight': 0.001,        # Positive weight
    'delay': 1.0,
    'sec': 'soma',
    'loc': 0.5
}

# Simulation Configuration
simConfig = specs.SimConfig()

simConfig.duration = 200.0
simConfig.dt = 0.025
simConfig.recordStep = 0.025
simConfig.verbose = False

simConfig.recordCells = [0, 1]
simConfig.recordTraces = {
    'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}
}

# Run Simulation
print("Creating network and running simulation (inhibitory synapses)...")
sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)
print("Simulation complete!")

# Extract Data
time = sim.allSimData['t']

if 'V_soma' in sim.allSimData and isinstance(sim.allSimData['V_soma'], dict):
    V_wide = sim.allSimData['V_soma'].get('cell_0', [])
    V_narrow = sim.allSimData['V_soma'].get('cell_1', [])
else:
    print("Error: Voltage data not available.")
    V_wide = []
    V_narrow = []

# Live Animation Setup (Updated for Inhibition)
fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlabel('Time (ms)', fontsize=12, fontweight='bold')
ax.set_ylabel('Membrane Potential (mV)', fontsize=12, fontweight='bold')
ax.set_title('Live Demo: Temporal Summation of Inhibitory Synapses (IPSPs)', fontsize=16, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 200)
ax.set_ylim(-110, -60)  # Adjusted to show hyperpolarization

line_wide, = ax.plot([], [], 'b-', linewidth=3, label='Wide Interval (minimal summation)')
line_narrow, = ax.plot([], [], 'r-', linewidth=3, label='Narrow Interval (strong summation)')
ax.legend(loc='lower right', fontsize=12)  # Legend position adjusted for downward traces

stim_lines = []
summation_patch = ax.axvspan(20, 35, alpha=0.15, color='yellow')
summation_patch.set_visible(False)

def init():
    line_wide.set_data([], [])
    line_narrow.set_data([], [])
    for sl in stim_lines:
        sl.remove()
    stim_lines.clear()
    summation_patch.set_visible(False)
    return [line_wide, line_narrow, summation_patch]

def update(frame):
    step = 16  # Animation speed
    idx = min(frame * step, len(time))
    
    line_wide.set_data(time[:idx], V_wide[:idx])
    line_narrow.set_data(time[:idx], V_narrow[:idx])
    
    dt = simConfig.dt
    if idx >= int(21 / dt) and len(stim_lines) < 1:
        stim_lines.append(ax.axvline(21, color='gray', linestyle='--', alpha=0.7, linewidth=2))
    if idx >= int(26 / dt) and len(stim_lines) < 2:
        stim_lines.append(ax.axvline(26, color='gray', linestyle='--', alpha=0.7, linewidth=2))
    if idx >= int(61 / dt) and len(stim_lines) < 3:
        stim_lines.append(ax.axvline(61, color='gray', linestyle='--', alpha=0.7, linewidth=2))
    
    if idx > 0 and 20 <= time[idx-1] <= 35:
        summation_patch.set_visible(True)
    else:
        summation_patch.set_visible(False)
    
    return [line_wide, line_narrow, summation_patch] + stim_lines

num_frames = (len(time) // 8) + 20
ani = FuncAnimation(fig, update, frames=num_frames, init_func=init,
                    blit=False, interval=80, repeat=True)

print("\nStarting live animation... The window will stay open and loop until you close it.")
plt.show()

