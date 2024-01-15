import FinanceDataReader as fdr
import datetime
import streamlit as st
import pandas as pd
import time
import pyupbit


st.set_page_config(layout="wide")
pw = st.text_input("비번을 넣으세요", type="password")
if pw == st.secrets["pw"] or pw == st.secrets["pwopen"]: 

    df = pd.DataFrame()
    
    def makeSignal(stock_symbol,maxCur1Rate,minCur1Rate):
        # 3배짜리 이면 배수를 1로 나누고 1배는 3으로 나눈다(변화량때문)
        times = 3
        if stock_symbol[-1] == ")":
            times = 1
        signal = ""
        if maxCur1Rate < -25/times and minCur1Rate < 60/times:
            signal = "구매가능(1단계)"
        elif maxCur1Rate < -40/times and minCur1Rate < 90/times:
            signal = "구매추천(2단계)"
        elif maxCur1Rate < -50/times and minCur1Rate < 120/times:
            signal = "구매(3단계)"
        elif maxCur1Rate < -60/times and minCur1Rate < 150/times:
            signal = "구매요망(4단계)"
        elif maxCur1Rate < -80/times and minCur1Rate < 200/times:
            signal = "강력구매(5단계)"
        else:
            signal = "관망"
        return signal
            
    # @st.cache_data(show_spinner="검색중", ttl="30m")
    def checkStock(ticker):
        global df
        stock_symbol = ticker.replace("(3X)","")
        start_date = datetime.date.today() - datetime.timedelta(365*3)
        end_date = datetime.date.today()
        stock_data = fdr.DataReader(stock_symbol, start_date, end_date)
    
        curPrice = stock_data.iloc[-1]['Close']
        max3Year = stock_data['Close'].max()
        max2Year = stock_data[(datetime.date.today() - datetime.timedelta(365*2)):]['Close'].max()
        max1Year = stock_data[(datetime.date.today() - datetime.timedelta(365*1)):]['Close'].max()
        min3Year = stock_data['Close'].min()
        min2Year = stock_data[(datetime.date.today() - datetime.timedelta(365*2)):]['Close'].min()
        min1Year = stock_data[(datetime.date.today() - datetime.timedelta(365*1)):]['Close'].min()
        maxCur3Rate = (curPrice-max3Year)/max3Year*100
        maxCur2Rate = (curPrice-max2Year)/max2Year*100
        maxCur1Rate = (curPrice-max1Year)/max1Year*100
        minCur1Rate = (curPrice-min1Year)/min1Year*100
        signal = makeSignal(ticker,maxCur1Rate,minCur1Rate)
    
        ind = [ticker,round(curPrice,2),round(max3Year,2),round(max2Year,2),round(max1Year,2),round(min3Year,2),round(min2Year,2),round(min1Year,2),round(maxCur3Rate,2),round(maxCur2Rate,2),round(maxCur1Rate,2),round(minCur1Rate,2),signal]
        column = ["종목","현재가","3년최고","2년최고","1년최고","3년최저","2년최저","1년최저","3년고비","2년고비","1년고비","1년저비","매수/매도 Signal"]
        # df = pd.DataFrame()
        if len(df) == 0:
            df = pd.DataFrame([ind],columns=column)
            df.set_index(keys='종목',inplace=True)
        else:
            df1 = pd.DataFrame([ind],columns=column)
            df1.set_index(keys='종목',inplace=True)
            df = pd.concat([df,df1])
    
    def checkBitCoin():
        global df
        ticker = "KRW-BTC"
        curPrice = pyupbit.get_current_price(ticker)
        dfbit = pyupbit.get_ohlcv(ticker, 'month',36)
        max3Year = dfbit['high'].max()
        max2Year = dfbit.iloc[12:]['high'].max()
        max1Year = dfbit.iloc[24:]['high'].max()
        min3Year = dfbit['low'].min()
        min2Year = dfbit.iloc[12:]['low'].min()
        min1Year = dfbit.iloc[24:]['low'].min()
        maxCur3Rate = (curPrice-max3Year)/max3Year*100
        maxCur2Rate = (curPrice-max2Year)/max2Year*100
        maxCur1Rate = (curPrice-max1Year)/max1Year*100
        minCur1Rate = (curPrice-min1Year)/min1Year*100
        signal = makeSignal(ticker,maxCur1Rate,minCur1Rate)
        ind = [ticker,round(curPrice,2),round(max3Year,2),round(max2Year,2),round(max1Year,2),round(min3Year,2),round(min2Year,2),round(min1Year,2),round(maxCur3Rate,2),round(maxCur2Rate,2),round(maxCur1Rate,2),round(minCur1Rate,2),signal]
        column = ["종목","현재가","3년최고","2년최고","1년최고","3년최저","2년최저","1년최저","3년고비","2년고비","1년고비","1년저비","매수/매도 Signal"]
        df1 = pd.DataFrame([ind],columns=column)
        df1.set_index(keys='종목',inplace=True)
        df = pd.concat([df,df1])
    
    checkList = ["TQQQ(3X)","TMF(3X)","FNGU(3X)","BULZ(3X)","LABU(3X)","LABD(3X)","UPRO(3X)","SOXL(3X)","SOXX","BNKU(3X)","SCHD","TSLY","QQQ","SPY","TSLA","AAPL","IBIT"]
    for i in checkList:
        # i = i.replace("(3X)","")
        checkStock(i)
        time.sleep(0.2)
    checkBitCoin()
    pd.set_option('display.max_colwidth', None)
    st.write(df.style.format({"현재가": "{:.2f}","3년최고": "{:.2f}","2년최고": "{:.2f}","1년최고": "{:.2f}","3년최저": "{:.2f}","2년최저": "{:.2f}",
                            "1년최저": "{:.2f}","3년고비": "{:.2f}","2년고비": "{:.2f}","1년고비": "{:.2f}","1년저비": "{:.2f}"}))
    # st.table(df)
