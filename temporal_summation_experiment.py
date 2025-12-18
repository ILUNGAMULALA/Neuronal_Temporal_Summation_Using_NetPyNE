"""
Temporal Summation Experiment using NetPyNE

This script demonstrates temporal summation by comparing two conditions:
1. Wide spike interval (20.0, 60.0 ms) - minimal summation
2. Narrow spike interval (20.0, 25.0 ms) - clear temporal summation

The results are shown in a live Matplotlib animation that builds the traces
progressively over time, simulating the process unfolding in real-time.
"""

# Import necessary modules
from netpyne import specs, sim
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib

# This fixes the issue where the plot window closes immediately on many Windows systems
matplotlib.use('TkAgg')  # Use TkAgg backend (works well on Windows for interactive plots)

# Network Parameters (netParams)
netParams = specs.NetParams()

# Cell Properties
netParams.cellParams['passive_cell'] = {
    'secs': {
        'soma': {
            'geom': {
                'diam': 18.8,
                'L': 18.8,
                'Ra': 123.0,
                'cm': 1.0
            },
            'mechs': {
                'pas': {
                    'g': 0.0000357,
                    'e': -70
                }
            },
            'vinit': -70
        }
    }
}

# Population Definitions
netParams.popParams['postPop'] = {
    'cellType': 'passive_cell',
    'numCells': 2,
    'cellModel': 'passive'
}

# Synapse Mechanisms
netParams.synMechParams['AMPA'] = {
    'mod': 'Exp2Syn',
    'tau1': 0.5,
    'tau2': 5.0,
    'e': 0
}

# Stimulation Sources
netParams.stimSourceParams['stimWide'] = {
    'type': 'NetStim',
    'start': 20.0,
    'interval': 40.0,
    'noise': 0,
    'number': 2
}

netParams.stimTargetParams['stimWide->post0'] = {
    'source': 'stimWide',
    'conds': {'pop': 'postPop', 'cellList': [0]},
    'synMech': 'AMPA',
    'weight': 0.001,
    'delay': 1.0,
    'sec': 'soma',
    'loc': 0.5
}

netParams.stimSourceParams['stimNarrow'] = {
    'type': 'NetStim',
    'start': 20.0,
    'interval': 5.0,
    'noise': 0,
    'number': 2
}

netParams.stimTargetParams['stimNarrow->post1'] = {
    'source': 'stimNarrow',
    'conds': {'pop': 'postPop', 'cellList': [1]},
    'synMech': 'AMPA',
    'weight': 0.001,
    'delay': 1.0,
    'sec': 'soma',
    'loc': 0.5
}

# Simulation Configuration (simConfig)
simConfig = specs.SimConfig()

simConfig.duration = 200.0
simConfig.dt = 0.025
simConfig.recordStep = 0.025
simConfig.verbose = False

simConfig.recordCells = [0, 1]
simConfig.recordTraces = {
    'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}
}

# Create and Run Simulation
print("Creating network and running simulation...")
sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)
print("Simulation complete!")

# Extract Data for Animation
time = sim.allSimData['t']

if 'V_soma' in sim.allSimData and isinstance(sim.allSimData['V_soma'], dict):
    V_wide = sim.allSimData['V_soma'].get('cell_0', [])
    V_narrow = sim.allSimData['V_soma'].get('cell_1', [])
else:
    print("Error: Voltage data not available.")
    V_wide = []
    V_narrow = []


# Live Animation Setup

fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlabel('Time (ms)', fontsize=12, fontweight='bold')
ax.set_ylabel('Membrane Potential (mV)', fontsize=12, fontweight='bold')
ax.set_title('Live Demo: Temporal Summation Over Time', fontsize=16, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 200)
ax.set_ylim(-75, -30)

line_wide, = ax.plot([], [], 'b-', linewidth=3, label='Wide Interval (40 ms apart)')
line_narrow, = ax.plot([], [], 'r-', linewidth=3, label='Narrow Interval (5 ms apart)')
ax.legend(loc='upper right', fontsize=12)

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
    step = 16  # Controls animation speed: If we increase this, the animation goes faster
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
                    blit=False, interval=80, repeat=True)  # blit=False is more reliable on Windows

print("\nStarting live animation... The window will stay open and loop until you close it.")
plt.show()  # This blocks until the window is closed

