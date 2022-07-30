import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np

##########################################################################
# MOMENTUM TRACKER

def main():
    # Create a DataFrame so 'ta' can be used.
    df = pd.DataFrame()
    symbol = input(("Stock to look up: "))
    stocks(symbol)

##########################################################################
# DEFINING A STOCK STRATEGY FUNCTION
def stocks(xxx):

    # Request pricing data via finance.yahoo.com API
    df = yf.Ticker(xxx).history(period='1y')
    #bull year test
    #df = yf.Ticker(xxx).history(start="2020-06-08", end="2021-06-07", interval="1d")
    #bear year test
    #df = yf.Ticker(xxx).history(start="2019-06-08", end="2020-06-07", interval="1d")
##########################################################################
    # GETTING MACD

    macd_list = df.ta.macd()
    macd_value = macd_momentum(macd_list)

##########################################################################
    # GETTING DISPARITY INDEX AND ISOLATION OPEN/CLOSE PRICES

    open = df['Open'].tolist()
    close = df['Close'].tolist()
    sma14 = df.ta.sma(length=14)
    di14, disparity_value, disparity_diff = di_14(sma14, close)

##########################################################################
    # GETTING RSI

    rsi_list = df.ta.rsi(close='close', length = 14)
    rsi_value = rsi_momentum(rsi_list)

##########################################################################
    # GETTING WILLIAMS %R

    r_list = df.ta.willr(close='close')
    willr_value = willr(r_list)
##########################################################################
    # GETTING BOLLINGER BAND

    bband_list = df.ta.bbands()
    bb_lower = bband_list.iloc[:, 0].tolist()
    bb_upper = bband_list.iloc[:, 2].tolist()
    bb_value = bband(bb_lower, bb_upper, open)
##########################################################################
    # CREATING AND ORGANIZING DATAFRAME
    del df["High"]
    del df["Low"]
    del df["Volume"]
    del df["Dividends"]
    del df["Stock Splits"]

    df["RSI"] = rsi_list
    rsi_diff = np.diff(rsi_list)
    rsi_diff =  np.insert(rsi_diff, 0,0)
    df['rsi diff'] = rsi_diff
    df["rsi_value"] = rsi_value

    df["MA 14"] = sma14
    df["DISPARITY INDEX"] = di14
    df['disparity diff']=disparity_diff
    df["disparity_value"] = disparity_value

    df["will r list"] = r_list
    df["will r value"] = willr_value

    df['macd list'] = macd_list.iloc[:, 1]
    df['macd value'] = macd_value

    df['BB low'] = bb_lower
    df['BB upper'] = bb_upper
    df['BBand value'] = bb_value

##########################################################################
    # CALCULATING 'TOTAL MOMENTUM'
    df['Total Momentum'] = total_momentum = df['disparity_value'] + df['rsi_value'] + df["will r value"] + df['macd value'] + df['BBand value']

    # CALCULATING BUY AND SELL SIGNAL
    signal_value, current_status = signal(total_momentum)
    df["Signal"] = signal_value

    # OVERNIGHT TRADING BECAUSE I TRADE AFTER HOURS SHIFT POSITION OVER 1
    df["Overnight Trading"] = df.Signal.shift(1)
    df['Current Status'] = current_status

    # CALCULATING BUY/SELL PRICE WITH AFTER HOURS TRADING SHIFT 1
    combine = list(zip(df["Overnight Trading"], open))
    buy_price, sell_price = overnight_trading(combine)
    df["Buy Price"] = buy_price
    df["Sell Price"] = sell_price

##########################################################################
    # PARTICULARS FOR VIEWING AND CHECKING BACK TESTING

    # PULL BUY/SELL OPENING VALUES INTO ONE COLUMN
    buy_sell = (df["Buy Price"].fillna(0) + df["Sell Price"].fillna(0))

    # REMOVING ZEROS IN BUY/SELL CONVERTING TO NP.NAN
    buy_sell = np.where(buy_sell == 0, np.nan, buy_sell)

    # REMOVING FIRST VALUE IF SELL AND LAST VALUE IF BUY, PULLING FIRST BUY VALUE INDEX
    first_value = buy_sell[np.isfinite(buy_sell)][0]
    last_value = buy_sell[np.isfinite(buy_sell)][-1]
    # if number is positive (SELL) remove data
    if first_value > 0:
        # change to 0
        buy_sell = np.where(buy_sell == first_value, 0, buy_sell)
    # if last number is negative (BUY) remove data
    if last_value < 0:
        buy_sell = np.where(buy_sell == last_value , 0, buy_sell)

    # get index position of first buy signal
    if "BUY" in current_status:
        second_value = current_status.index("BUY")+1
    else:
        second_value = 0

    df['Buy/Sell Combo'] = buy_sell

##########################################################################
    # DEFINE POSITION (ASSUME HOLDING IF IN BUY MODE/ NOT HOLDING IF IN SELL MODE) // ADDING TO DATAFRAME
    df["Position"] = position(df["Overnight Trading"], open)

##########################################################################
    # BACKTESTING CALCULATIONS

    # CALC DIFF OF OPENING FROM TODAY - YESTERDAY SHIFTED UP
    n = np.diff(df.Open.shift(0))

    ##IndexError: index 251 is out of bounds for axis 0 with size 250
    price_diff = np.insert(n, 250, 0)
    df["Opening Price Difference"] = price_diff

    # getting Future Open Percent Change from current day
    df['Opening Price Diff %'] = df["Opening Price Difference"] / df['Open']

    # CALC RETURNS BASED ON IF HOLDING STOCK
    the_returns = df["Opening Price Difference"] * df["Position"]
    strat_ret = the_returns
    df['Strategy Returns'] = strat_ret

    # INVESTMENT VALUE AND STOCKS HOLDING BASED ON VALUE
    investment_value = 500
    number_of_stocks = investment_value/df["Open"][second_value]

    # CALC RETURN BASED ON NUMBER OF STOCKS HELD
    investment_returns = number_of_stocks * df["Strategy Returns"]
    df["Strategy x Stock Holdings"] = investment_returns

    # PROFIT AND PERCENT FINAL CALC
    total_investment = round(sum(investment_returns), 2)
    profit_percentage = (total_investment/investment_value)*100
    # FIGURE OUT HOW TO COMPOUND ADD EARNINGS FROM PREVIOUS BUY TIMES TO NEW BUY TIMES
    print (f'For one year with a ${investment_value} investment, the return is ${total_investment} a {profit_percentage}% difference')

    # EXPORT TO CSV
    df.to_csv('strategy.csv')

    return total_investment, profit_percentage

##########################################################################
# APPLYING THE STRATEGIES INTO A BUY/SELL SIGNAL

def signal(data):
    signal = 0
    signal_data = []
    current_status = []
    for element in data:
        if element >= 30:
            if signal != 1:
                signal = 1
                signal_data.append(signal)
                current_status.append("BUY")
            else:
                signal_data.append(0)
                current_status.append(np.nan)
        elif element < -10:
            if signal != -1:
                signal = -1
                signal_data.append(signal)
                current_status.append("SELL")
            else:
                signal_data.append(0)
                current_status.append(np.nan)
        else:
            signal_data.append(0)
            current_status.append(np.nan)
    return signal_data, current_status

##########################################################################
# Disparity Index Momentum 34

def di_14(sma14, close):
    # calc disparity index and the values for algo
    disparity_index = []
    disparity_value = []
    combined = list(zip(sma14, close))
    # iterate over list
    for i in combined:
        # assign variables
        sma14 = i[0] ; close = i[1]
        di = ((close - sma14) / sma14) * 100
        disparity_index.append(di)

    d_index_diff = np.diff(disparity_index)
    d_index_diff = np.insert(d_index_diff, 0,0)

    for i in d_index_diff:
        if i >= 0:
            # bullish return
            disparity_value.append(10)
        elif i < 0:
            # bearish return
            disparity_value.append(-10)
        else:
            disparity_value.append(0)

    return disparity_index, disparity_value, d_index_diff

##########################################################################
# Catching RSI Bearish/Bullish rally 31

def rsi_momentum(data):
    rsi_array = []
    rsi_array.insert(0,0)
    for minus1, cur in zip(data, data [1:]):
        if minus1<cur and (cur-minus1)>=.5:
        # bull
            rsi_array.append(10)
        # bear
        elif minus1>cur:
            rsi_array.append(-10)
        else:
            rsi_array.append(0)
    return rsi_array

##########################################################################
# Catching MACD 13

def macd_momentum(data):

    macdh = data.iloc[:, 1].tolist()

    macd_array = []
    macd_array.insert(0,0)

    # tracking movement
    for minus1, cur in zip(macdh, macdh [1:]):
        # bullish
        if minus1<0 and -5<cur<5 and minus1<cur:
            macd_array.append(10)
        #bear
        #elif minus1>cur:
        elif cur <0:
            macd_array.append(-10)
        else:
            macd_array.append(0)
    return macd_array
##########################################################################
# Williams %R momentum 16

def willr(data):
    willr_array = []
    willr_array.insert(0,0)
    for minus1, cur in zip(data, data [1:]):
        # bullish
        if -70<=minus1<=-40 and minus1<cur :
            willr_array.append(10)
        # bearish
        elif minus1>cur:
            willr_array.append(-10)
        else:
            willr_array.append(0)
    return willr_array
##########################################################################
# Bollinger Band

def bband(lower, upper, open):
    bb_array = []
    for low, upp, opn in zip(lower, upper, open):
        # bullish
        if opn<low:
            bb_array.append(10)
        # bearish
        elif opn>upp:
            bb_array.append(-10)
        else:
            bb_array.append(0)
    return bb_array
##########################################################################
# CREATING A POSITION OF HOLDING/NOT HOLDING FOR BACKTESTING

def position(signal, open):
    position = []
    for i in range(len(signal)):
        if signal[i] > 1:
            position.append(1)
        else:
            position.append(0)

    for i in range(len(open)):
        if signal[i] == 1:
            position[i] = 1
        elif signal[i] == -1:
            position[i] = 0
        else:
            position[i] = position[i-1]
    return position

##########################################################################
# PROCESS SIGNAL FOR OVERNIGHT TRADING

def overnight_trading(data):
    buy_price = []
    sell_price = []
    for i in data:
        signal_o = i[0] ; open = i[1]
        if signal_o == 1:
            buy_price.append(-abs(open))
            sell_price.append(np.nan)
        elif signal_o == -1:
            buy_price.append(np.nan)
            sell_price.append(open)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
    return buy_price, sell_price

##########################################################################

if __name__ == "__main__":
    main()
