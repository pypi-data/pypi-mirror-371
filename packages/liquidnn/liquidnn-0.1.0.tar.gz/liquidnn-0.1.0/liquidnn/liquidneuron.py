import torch
import torch.nn as nn

class LiquidNeuron(nn.Module):
    def __init__(self, input_size, hidden_size):
        super().__init__()
        self.hidden_size = hidden_size
        self.W = nn.Parameter(torch.randn(hidden_size, hidden_size) * 0.05)
        self.U = nn.Parameter(torch.randn(hidden_size, input_size) * 0.05)
        self.alpha = nn.Parameter(torch.randn(hidden_size, hidden_size) * 0.01)
        self.bias = nn.Parameter(torch.randn(hidden_size))

    def forward(self, x, h):
        device = x.device
        h_new = torch.tanh(torch.matmul(h, self.W.T) +torch.matmul(x, self.U.T) +torch.matmul(h, self.alpha.T) +self.bias).to(device)
        return h_new


class LiquidNeuronv2(nn.Module):
    def __init__(self, input_size, hidden_size,scaling_factor_W,scaling_factor_U,scaling_factor_alpha):
        super().__init__()
        self.hidden_size = hidden_size
        self.W = nn.Parameter(torch.randn(hidden_size, hidden_size) * scaling_factor_W)
        self.U = nn.Parameter(torch.randn(hidden_size, input_size) * scaling_factor_U)
        self.alpha = nn.Parameter(torch.randn(hidden_size, hidden_size) * scaling_factor_alpha)
        self.bias = nn.Parameter(torch.randn(hidden_size))

    def forward(self, x, h):
        device = x.device
        h_new = torch.tanh(torch.matmul(h, self.W.T) +torch.matmul(x, self.U.T) +torch.matmul(h, self.alpha.T) +self.bias).to(device)
        return h_new