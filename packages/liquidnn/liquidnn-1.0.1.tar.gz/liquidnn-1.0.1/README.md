# liquidnn

**liquidnn** is a PyTorch library for **Liquid Neural Networks (LNNs)**, including multi-layer networks built from liquid neurons.  
This library provides an easy interface to use liquid dynamics in your neural networks without needing to handle the underlying neurons directly.

---

## Installation

```bash
pip install liquidnn


Usage

import torch
from liquidnn import LiquidNeuralNetwork

# Example: batch=2, seq_len=5, input_size=10
x = torch.randn(2, 5, 10)

# Initialize a multi-layer liquid neural network
model = LiquidNeuralNetwork(
    input_size=10,
    hidden_size=20,
    num_layers=2,          # number of stacked liquid layers
    tau=0.5,               # temporal integration factor
    scaling_factor_W=0.05, # weight scaling factor
    scaling_factor_U=0.05,
    scaling_factor_alpha=0.05
)

# Forward pass
out = model(x)
print(out.shape)  # Expected: torch.Size([2, 20])



Parameters

LiquidNeuralNetwork:

input_size (int): Number of input features per timestep.

hidden_size (int): Size of each liquid layer’s hidden state.

num_layers (int, default=1): Number of stacked liquid layers.

tau (float, default=0.5): Temporal integration factor controlling neuron update speed.

scaling_factor_W/U/alpha (float, default=0.05): Scaling factors for internal neuron parameters.

Features

Multi-layer liquid neural networks for sequential data.

Continuous-time neuron update using tau.

Fully compatible with PyTorch modules.

Users can import only LiquidNeuralNetwork; internal neurons are private.



References

--> https://arxiv.org/pdf/2006.00232