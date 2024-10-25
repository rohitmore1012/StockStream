import streamlit as st
import pandas as pd
import datetime
from datetime import date
from plotly import graph_objs as go
from plotly.subplots import make_subplots
from prophet import Prophet
from prophet.plot import plot_plotly
import time
from streamlit_option_menu import option_menu
import os
os.environ["YFINANCE_CACHE_DIR"] = "/tmp"
import yfinance as yf


st.set_page_config(layout="wide", initial_sidebar_state="expanded")

def add_meta_tag():
    meta_tag = """
        <head>
            <meta name="google-site-verification" content="QBiAoAo1GAkCBe1QoWq-dQ1RjtPHeFPyzkqJqsrqW-s" />
        </head>
    """
    st.markdown(meta_tag, unsafe_allow_html=True)

add_meta_tag()

today = date.today()
st.write('''# StockStream ''')
st.sidebar.image("Images/StockStreamLogo1.png", width=250, use_column_width=False)
st.sidebar.write('''# StockStream ''')

with st.sidebar:
    selected = option_menu("Utilities", ["Stocks Performance Comparison", "Real-Time Stock Price", "Stock Prediction", 'About'])

start = st.sidebar.date_input('Start', datetime.date(2022, 1, 1))
end = st.sidebar.date_input('End', datetime.date.today())

stock_df = pd.read_csv("StockStreamTickersData.csv")

if selected == 'Stocks Performance Comparison':
    st.subheader("Stocks Performance Comparison")
    tickers = stock_df["Company Name"]
    dropdown = st.multiselect('Pick your assets', tickers)

    with st.spinner('Loading...'):
        time.sleep(2)

    dict_csv = pd.read_csv('StockStreamTickersData.csv', header=None, index_col=0).to_dict()[1]
    symb_list = [dict_csv.get(i) for i in dropdown]

    def relativeret(df):
        rel = df.pct_change()
        cumret = (1 + rel).cumprod() - 1
        return cumret.fillna(0)

    if dropdown:
        df = relativeret(yf.download(symb_list, start, end))['Adj Close']
        raw_df = relativeret(yf.download(symb_list, start, end)).reset_index()

        closingPrice = yf.download(symb_list, start, end)['Adj Close']
        volume = yf.download(symb_list, start, end)['Volume']
        
        st.subheader(f'Raw Data {dropdown}')
        st.write(raw_df)
        chart = ('Line Chart', 'Area Chart', 'Bar Chart')
        dropdown1 = st.selectbox('Pick your chart', chart)

        with st.spinner('Loading...'):
            time.sleep(2)

        st.subheader(f'Relative Returns {dropdown}')
        
        if dropdown1 == 'Line Chart':
            st.line_chart(df)
            st.write(f"### Closing Price of {dropdown}")
            st.line_chart(closingPrice)
            st.write(f"### Volume of {dropdown}")
            st.line_chart(volume)

        elif dropdown1 == 'Area Chart':
            st.area_chart(df)
            st.write(f"### Closing Price of {dropdown}")
            st.area_chart(closingPrice)
            st.write(f"### Volume of {dropdown}")
            st.area_chart(volume)

        elif dropdown1 == 'Bar Chart':
            st.bar_chart(df)
            st.write(f"### Closing Price of {dropdown}")
            st.bar_chart(closingPrice)
            st.write(f"### Volume of {dropdown}")
            st.bar_chart(volume)
    else:
        st.write('Please select at least one asset')

elif selected == 'Real-Time Stock Price':
    st.subheader("Real-Time Stock Price")
    tickers = stock_df["Company Name"]
    a = st.selectbox('Pick a Company', tickers)

    with st.spinner('Loading...'):
        time.sleep(2)

    dict_csv = pd.read_csv('StockStreamTickersData.csv', header=None, index_col=0).to_dict()[1]
    symb_list = [dict_csv.get(a)]

    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = False

    def callback():
        st.session_state.button_clicked = True

    if st.button("Search", on_click=callback) or st.session_state.button_clicked:
        if not a:
            st.write("Click Search to Search for a Company")
        else:
            data = yf.download(symb_list, start=start, end=end)
            data.reset_index(inplace=True)
            st.subheader(f'Raw Data of {a}')
            st.write(data)

            def plot_raw_data():
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
                fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
                fig.layout.update(title_text=f'Line Chart of {a}', xaxis_rangeslider_visible=True)
                st.plotly_chart(fig)

            def plot_candle_data():
                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=data['Date'], open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='market data'))
                fig.update_layout(title=f'Candlestick Chart of {a}', yaxis_title='Stock Price', xaxis_title='Date')
                st.plotly_chart(fig)

            chart = ('Candle Stick', 'Line Chart')
            dropdown1 = st.selectbox('Pick your chart', chart)
            if dropdown1 == 'Candle Stick':
                plot_candle_data()
            elif dropdown1 == 'Line Chart':
                plot_raw_data()

elif selected == 'Stock Prediction':
    st.subheader("Stock Prediction")
    tickers = stock_df["Company Name"]
    a = st.selectbox('Pick a Company', tickers)

    with st.spinner('Loading...'):
        time.sleep(2)

    dict_csv = pd.read_csv('StockStreamTickersData.csv', header=None, index_col=0).to_dict()[1]
    symb_list = [dict_csv.get(a)]

    if a:
        data = yf.download(symb_list, start=start, end=end)
        data.reset_index(inplace=True)
        st.subheader(f'Raw Data of {a}')
        st.write(data)

        def plot_raw_data():
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
            fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
            fig.layout.update(title_text=f'Time Series Data of {a}', xaxis_rangeslider_visible=True)
            st.plotly_chart(fig)

        plot_raw_data()

        n_years = st.slider('Years of prediction:', 1, 4)
        period = n_years * 365

        df_train = data[['Date', 'Close']].rename(columns={"Date": "ds", "Close": "y"})
        m = Prophet()
        m.fit(df_train)
        future = m.make_future_dataframe(periods=period)
        forecast = m.predict(future)

        st.subheader(f'Forecast Data of {a}')
        st.write(forecast)

        st.subheader(f'Forecast plot for {n_years} years')
        fig1 = plot_plotly(m, forecast)
        st.plotly_chart(fig1)

        st.subheader(f"Forecast components of {a}")
        fig2 = m.plot_components(forecast)
        st.write(fig2)

elif selected == 'About':
    st.subheader("About")
    
    st.markdown("""
        <style>
            .big-font { font-size:25px !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="big-font">StockStream is a web application for stock performance comparison, real-time stock prices, and prediction, developed using Streamlit. Created by Vaishnavi Sharma and Rohit More.</p>', unsafe_allow_html=True)
    st.subheader('Rohit More [GitHub](https://github.com/rohitmore1012)')
    st.subheader('Vaishnavi Sharma [GitHub](https://github.com/vaishnavi3131)')
