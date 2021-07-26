import pandas as pd

def load_tradingview_csv(filename, drop_last_bar=false):
    df = pd.read_csv(filename)

    # drop unsed column
    if 'Volume MA' in df:
        df.drop(columns=['Volume MA'], inplace=True)
    
    # rename columns
    df.columns=['date', 'open', 'high', 'low', 'close', 'volume']

    # convert the time column type from string to datetime for proper sorting.
    df['date']=pd.to_datetime(df['date'])

    # Make sure historical prices are sorted chronologically, oldest first.
    df.sort_values(by='date', ascending=True, inplace=True)

    # drop last data row (bar might yet close, drop it for data accuracy)
    if drop_last_bar:
        df.drop(df.tail(1).index, inplace=True) # drop last

    # reset index
    df.reset_index(drop=True, inplace=True)

    return df