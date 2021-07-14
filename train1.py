import ta
from ta.trend import *

import pandas as pd
import numpy as np

from tensortrade.feed.core import Stream, DataFeed, NameSpace
from tensortrade.oms.exchanges import Exchange
from tensortrade.oms.services.execution.simulated import execute_order
from tensortrade.oms.instruments import Instrument, USD, BTC
from tensortrade.oms.wallets import Wallet, Portfolio
from tensortrade.env.default.renderers import PlotlyTradingChart, FileLogger
import tensortrade.env.default as default
from tensortrade.agents import DQNAgent

import matplotlib.pyplot as plt

from transform import difference, log_and_difference, max_min_normalize, mean_normalize

TTC = Instrument("TTC", 8, "TensorTrade Coin")


def generate_sine(amp=50, offset=100, cycle=3, steps=1000):
    """
    Generate sine wave DataFrame
    :param amp: amplitude
    :param offset: DC offset
    :param cycle: sine wave cycle
    :param steps: total steps
    :return: DataFrame
    """
    x = np.arange(0, 2 * np.pi, 2 * np.pi / (steps))
    y = amp * np.sin(cycle * x) + offset

    df = pd.DataFrame()
    df['close'] = y
    return df


def add_indicators(df, fillna=False):
    """
    Add indicators to DataFrame
    :param df: DataFrame
    :param fillna: Fill NA
    :return:
    """
    df['close_diff'] = difference(df['close'], inplace=False)
    df['close_log_diff'] = log_and_difference(df['close'], inplace=False)
    df['close_mean'] = mean_normalize(df['close'], inplace=False)

    df['macd_diff'] = macd_diff(df['close'], fillna=fillna)

    df['ema10'] = ema_indicator(df['close'], 10, fillna=fillna)
    df['ema25'] = ema_indicator(df['close'], 25, fillna=fillna)
    df['ema50'] = ema_indicator(df['close'], 50, fillna=fillna)

    df['ema25_50_diff'] = df['ema25'] - df['ema50']
    df['ema25_50_diff_norm'] = 1 - df['ema50'] / df['ema25']
    df['trend_ema25_50'] = np.where(df['ema25_50_diff'] > 0, 1, -1)

    df['ema10_25_diff'] = df['ema10'] - df['ema25']
    df['ema10_25_diff_norm'] = 1 - df['ema25'] / df['ema10']
    df['trend_ema10_25'] = np.where(df['ema10_25_diff'] > 0, 1, -1)

    df.dropna(axis=0, inplace=True)
    df.reset_index(drop=True, inplace=True)


def show_chart(df, columns1, columns2, columns3, title):

    fig, axs = plt.subplots(1, 3, figsize=(15, 3))
    fig.suptitle(title)

    df[columns1].plot(ax=axs[0], grid=True)
    df[columns2].plot(ax=axs[1], grid=True)
    df[columns3].plot(ax=axs[2], grid=True)

    plt.interactive(True)
    plt.show(block=True)


def show_performance(performance_df, price_history_df):
    fig, axs = plt.subplots(1, 2, figsize=(15, 7))
    fig.suptitle('Performance')

    performance_df.plot(ax=axs[0], grid=True, fontsize=12)
    performance_df.net_worth.plot(ax=axs[1], grid=True, legend=True)
    price_history_df['close'].plot(ax=axs[1], secondary_y=True, grid=True, legend=True)

    plt.interactive(True)
    plt.show(block=True)


if __name__ == '__main__':
    # sine wave parameters
    cycle = 2
    steps = 1000
    amplitude = 50
    dc_offset = 100

    # create data
    df = generate_sine(amp=amplitude, offset=dc_offset, cycle=cycle, steps=steps)

    # add indicators to data frame
    add_indicators(df, fillna=False)

    # data steps
    total_data_steps = len(df)
    print(f'Total data steps = {total_data_steps}')

    # create price history data frame
    price_history = df[['close']]

    # show chart
    columns1 = ['close']
    columns2 = ['ema10_25_diff', 'ema25_50_diff']
    columns3 = ['close_diff', 'trend_ema10_25', 'trend_ema25_50', 'macd_diff']
    # show_chart(df, columns1, columns2, columns3, 'df')

    # create stream based on 'close'
    close = Stream.source(price_history['close'].tolist(), dtype="float").rename("USD-TTC")

    # create data feed
    data_feed = DataFeed([
        # Stream.source(df['close'].tolist(), dtype="float").rename("price"),
        # Stream.source(df['close'].tolist(), dtype="float").diff().fillna(0).rename("price_diff"),
        # Stream.source(df['close'].tolist(), dtype="float").log().diff().fillna(0).rename("price_log_diff"),
        # Stream.source(df['ema25_50_diff_norm'].tolist(), dtype="float").rename("ema25_50_diff_norm"),
        Stream.source(df['close_diff'].tolist(), dtype="float").rename("close_diff"),

        # Stream.source(df['ema10_25_diff'].tolist(), dtype="float").rename("ema10_25_diff"),
        # Stream.source(df['trend_ema10_25'].tolist(), dtype="float").rename("trend_ema10_25"),

        Stream.source(df['ema25_50_diff'].tolist(), dtype="float").rename("ema25_50_diff"),
        Stream.source(df['trend_ema25_50'].tolist(), dtype="float").rename("trend_ema25_50"),

        # Stream.source(df['macd_diff'].tolist(), dtype="float").rename("macd_diff"),
    ])

    # create renderer feed
    renderer_feed = DataFeed([
        Stream.source(price_history[c].tolist(), dtype="float").rename(c) for c in price_history]
    )

    # setup renderer
    chart_renderer = PlotlyTradingChart(
        display=True,  # show the chart on screen (default)
        height=800,  # affects both displayed and saved file height. None for 100% height.
        save_format="html",  # save the chart to an HTML file
        auto_open_html=True,  # open the saved HTML chart in a new browser tab
    )

    file_logger = FileLogger(
        filename="example.log",  # omit or None for automatic file name
        path="training_logs"  # create a new directory if doesn't exist, None for no directory
    )

    # create exchange
    bitfinex = Exchange("bitfinex", service=execute_order)(
        close
    )

    # create portfolio
    initial_capital = 1000
    cash = Wallet(bitfinex, initial_capital * USD)
    asset = Wallet(bitfinex, 0 * TTC)

    portfolio = Portfolio(USD, [
        cash,
        asset
    ])

    # setup reward & action scheme
    from BSH import BSH
    from PBR import PBR

    reward_scheme="risk-adjusted"
    action_scheme="managed-risk"

    #reward_scheme = PBR(price=close)
    #action_scheme = BSH(cash=cash, asset=asset).attach(reward_scheme)

    # setup environment
    from PositionChangeChart import PositionChangeChart

    window_size = 25

    # env = default.create(
    #     portfolio=portfolio,
    #     action_scheme=action_scheme,
    #     reward_scheme=reward_scheme,
    #     feed=data_feed,
    #     window_size=window_size,
    #     renderer_feed=renderer_feed,
    #     renderer=PositionChangeChart()
    # )

    env = default.create(
        portfolio=portfolio,
        action_scheme=action_scheme,
        reward_scheme=reward_scheme,
        window_size=window_size,
        feed=data_feed,
        renderer=["screen-log"]
    )

    # setup agent
    n_episodes = 10
    n_steps = total_data_steps
    render_interval = 100

    agent = DQNAgent(env)

    # train agent
    # Set render_interval to None to render at episode ends only
    agent.train(n_episodes=n_episodes, n_steps=n_steps, render_interval=render_interval)

    # plot result
    performance = pd.DataFrame.from_dict(env.action_scheme.portfolio.performance, orient='index')
    performance.drop(['bitfinex:/USD-TTC'], axis=1, inplace=True)
    show_performance(performance, df)

    # output summary
    net_worth = performance.net_worth[len(performance.net_worth) - 1]
    print(f"Net worth = {net_worth} USD")

    pnl = 100 * (net_worth / initial_capital - 1)
    print(f"P&L = {pnl} %")
