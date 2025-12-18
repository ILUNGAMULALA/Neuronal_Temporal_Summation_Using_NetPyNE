# Temporal Summation Experiment using NetPyNE

## Overview

This project demonstrates **temporal summation** in a single-compartment postsynaptic neuron using **NetPyNE**. The simulation compares two conditions:

1. **Wide spike interval**: presynaptic spikes at 20 ms and 60 ms → minimal overlap.
2. **Narrow spike interval**: presynaptic spikes at 20 ms and 25 ms → clear temporal summation.

The results are visualized using a **live Matplotlib animation** that progressively builds the membrane potential traces over time.

---

## Requirements
- You should have NEURON
- Python 3.8+
- [NetPyNE](https://www.neurosimlab.org/netpyne/) (installed via `pip install netpyne`)
- Matplotlib (`pip install matplotlib`)

> **Note**: The script uses the `TkAgg` backend for interactive plotting on Windows. Ensure Tkinter is installed.

---

## Files

- `temporal_summation.py` — Main Python script for the simulation and animation.
- `README.md` — This file.

---

## How to Run

1. Open a terminal or command prompt.
2. Navigate to the directory containing the script.
3. Run:

```bash
python temporal_summation.py
