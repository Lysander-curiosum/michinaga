"""
The TEAnet model, for stock market analysis.
"""

from torch import nn, tensor
import torch
from michinaga.src.utils import classicAttention, temporal
from einops import repeat

class textEncoder(nn.Module):
    def __init__(self, num_heads, dim) -> None:
        super().__init__()
        self.multiHeadAttention = classicAttention(num_heads, dim)
        self.layernorm = nn.LayerNorm(dim)
        self.FFN = nn.Sequential(nn.Linear(dim, dim), nn.ReLU(), nn.Linear(dim, dim))
        self.attention = classicAttention(1, dim)

    """
    Function for the input into the text encoder. We feed in the tweet information (or other information streams)
    After the forward process executes, then we feed the remainder into the LSTM.
    """
    def forward(self, input):
        inter = self.multiHeadAttention.forward(input)
        new = self.layernorm(inter + input)
        output = self.FFN(new)
        return self.attention.forward(output)

"""
teanet 
long range dependencies for trend and price analysis

args:
    - num_heads
        The number of attention heads for the text encoder
    - dim
        The dimension of the message embeddings (what will they be projected into)
    - batch size 
        How many inputs are being processed at once

    DEPRECATED
    - k 
        How many messages will be considered for each trading day
        Because of the nature of the data that we are working with, 
        this value will be one for now (the embedded tweets averaged)

    - lag 
        How many prior trading days are being considered with each input
    - tweets 
        Tweet embeddings for all of the trading days in the lag period
    - prices
        normalized prices for all of the trading days in the lag period
"""


class teanet(nn.Module):
    def __init__(self, num_heads, dim, num_classes, batch_size, lag) -> None:
        super().__init__()
        self.dim = dim
        self.num_classes = num_classes
        self.pos_embed = nn.Parameter(torch.randn(1, lag, dim))
        self.lag = lag
        self.batch_size = batch_size
        """
        consider increasing the number of encoder blocks, to stabilize performance
        """
        self.textEncoder = textEncoder(num_heads, dim)
        self.lstm = nn.LSTM(input_size = 104, hidden_size = 5)
        self.temporal = temporal(109, num_classes, batch_size)

    """
    This should be dynamic based on the input from the user
    """
    def setBatchSize(self, new):
        self.batch_size = new
        self.temporal.setBatchSize(new)

    def forward(self, input):
        toFeed = input[0] + repeat(self.pos_embed, 'n d w -> (b n) d w', b = self.batch_size)
        lstm_text_input = self.textEncoder.forward(toFeed)
        lstm_in = torch.cat((lstm_text_input, input[1]), 2)
        out = self.lstm(lstm_in)
        lstm_copy = lstm_in
        final = self.temporal.forward(torch.cat((lstm_copy, out[0]), 2))
        return final


