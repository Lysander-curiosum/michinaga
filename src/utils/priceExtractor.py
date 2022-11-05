import torch 

"""
The price extractor, for preparing the price data input into the model. 
"""

class priceExtractor():
    """In the original TEANet model, the authors use attention to reach back 5 days for each 
    stock analyzed. The purpose of this initial model is to identify trends, specifically stocks 
    that are entering bullish trends."""
    def __init__(self, dim, batch_size, closing_prices, high_prices, low_prices):
        super(priceExtractor, self).__init__()
        self.dim = dim
        self.batch_size = batch_size
        self.closing_prices = closing_prices
        self.high_prices = high_prices
        self.low_prices = low_prices
        self.price_vector = torch.cat(self.closing_prices, self.high_prices, self.low_prices)
        self.price_vector = torch.div(self.price_vector, self.closing_prices) - 1

        
    def forward(self, x):
        return self.price_vector
