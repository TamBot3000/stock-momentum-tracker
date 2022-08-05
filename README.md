# Stock Momentum Tracker

A stock backtesting program that tests a custom stock strategy. Create an optimal strategy for today's markets.
- Type in one stock for backtesting with current strategy.
- Customize your own strategy.
- Test strategy with SP100 or SP500 tickers.
- Backtest your stock strategy with any time frame.


## Installation

- Use the latest version of python.
- Download or copy the code from the Stock Momentum Tracker.
- Please use [pip](https://pip.pypa.io/en/stable/) to install the following four libraries:
```bash
pip install yfinance
```
```bash
pip install pandas
```
```bash
pip install pandas-ta
```
```bash
pip install numpy
```


## Simple Usage

Once the four libraries are installed as shown:
```python
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
```

You're ready to go! Here's an example in the terminal:
```sh
$ python project.py
Stock to look up: goog
For one year with a $500 investment, the return is $57.76 a 11.552% difference
```


## Fun Features!

- Customize your timeframe or pick one of the preset timeframes for backtesting.
```sh
    # Request pricing data via finance.yahoo.com API
    df = yf.Ticker(xxx).history(period='1y')

    # bull year test
    # df = yf.Ticker(xxx).history(start="2020-06-08", end="2021-06-07", interval="1d")
    # bear year test
    # df = yf.Ticker(xxx).history(start="2019-06-08", end="2020-06-07", interval="1d")
```

- For testing multiple quotes, bypass the input and create a new list of stocks to check:
```sh
def main():
    # Create a DataFrame so 'ta' can be used.
    df = pd.DataFrame()
    # create a list of stocks to check...
    symbol = ['GOOG', 'AAPL', 'MSFT']
    for i in symbol:
        stocks(i)
```

- Browse the indicators that can be pulled via the  [pandas_ta](https://github.com/twopirllc/pandas-ta) library.

- Overnight trading function added for after-hours buying and selling.

- Export a custom DataFrame to a CSV file for further information on the stock you're testing.

## Contributing
Pull requests are welcome and encouraged.

Feel free to send me a message on [github](https://github.com/TamBot3000) with any questions.
