import streamlit as st
import pandas as pd
import datetime
from datetime import date
import time
from streamlit_option_menu import option_menu
import os
import yfinance as yf

# Set cache directory for yfinance
os.environ["YFINANCE_CACHE_DIR"] = "/tmp"

# Streamlit configuration
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Function to add meta tag
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

start = st.sidebar.date_input('Start', datetime.date(2015, 1, 1))
end = st.sidebar.date_input('End', datetime.date.today())

stock_df = pd.read_csv("StockStreamTickersData.csv")

def plot_lightweight_chart(data, title):
    """Create and display a Lightweight Chart."""
    chart_data = [
        {"time": row["Date"].strftime("%Y-%m-%d"), "value": row["Close"]}
        for index, row in data.iterrows()
    ]
    
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
    </head>
    <body>
        <div id="chart" style="width: 100%; height: 400px;"></div>
        <script>
            const chart = LightweightCharts.createChart(document.getElementById('chart'), {{
                width: 600,
                height: 400,
                layout: {{
                    backgroundColor: '#ffffff',
                    textColor: '#000'
                }},
            }});

            const lineSeries = chart.addLineSeries();
            lineSeries.setData({chart_data});
        </script>
    </body>
    </html>
    """
    st.components.v1.html(html_code, height=450)

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
        
        st.subheader(f'Raw Data {dropdown}')
        st.write(raw_df)

        if dropdown:
            st.subheader(f'Relative Returns {dropdown}')
            plot_lightweight_chart(df.reset_index(), 'Relative Returns')

            closingPrice = yf.download(symb_list, start, end)['Adj Close']
            st.write(f"### Closing Price of {dropdown}")
            plot_lightweight_chart(closingPrice.reset_index(), 'Closing Price')

            volume = yf.download(symb_list, start, end)['Volume']
            st.write(f"### Volume of {dropdown}")
            plot_lightweight_chart(volume.reset_index(), 'Volume')
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

            st.subheader(f'Line Chart of {a}')
            plot_lightweight_chart(data, 'Line Chart')

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

        st.subheader(f'Line Chart of {a}')
        plot_lightweight_chart(data, 'Line Chart')

        n_years = st.slider('Years of prediction:', 1, 4)
        period = n_years * 365

        df_train = data[['Date', 'Close']].rename(columns={"Date": "ds", "Close": "y"})
        m = Prophet()
        m.fit(df_train)
        future = m.make_future_dataframe(periods=period)
        forecast = m.predict(future)

        st.subheader(f'Forecast Data of {a}')
        st.write(forecast)

        # Plot forecast (use Lightweight Charts or create a separate function for the forecast plot)
        st.subheader(f'Forecast plot for {n_years} years (use Plotly for forecasting)')
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
