import torch
import torch.nn as nn
from .liquidneuron import LiquidNeuron

class LiquidNeuralNetwork(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, tau: float = 0.5,
                 scaling_factor_W: float = 0.05, scaling_factor_U: float = 0.05,
                 scaling_factor_alpha: float = 0.05, num_layers: int = 1):
        super().__init__()
        self.num_layers = num_layers
        self.layers = nn.ModuleList([
            LiquidNeuron(
                input_size if i == 0 else hidden_size,
                hidden_size,
                tau=tau,
                scaling_factor_W=scaling_factor_W,
                scaling_factor_U=scaling_factor_U,
                scaling_factor_alpha=scaling_factor_alpha
            ) for i in range(num_layers)
        ])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch, seq_len, input_size)
        returns: (batch, hidden_size) -> last hidden layer output
        """
        h_list = [None] * self.num_layers

        for t in range(x.size(1)):
            x_t = x[:, t, :]
            for l, layer in enumerate(self.layers):
                h_list[l] = layer(x_t, h_list[l])
                x_t = h_list[l]  # pass output to next layer

        return h_list[-1]
