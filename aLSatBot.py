import streamlit as st
from datetime import datetime
import json
from requests import Session
from tradingview_ta import *
import concurrent.futures

class Crypto_analysis:
    
    all=[]
    interval=""
    osc_coins={}
    buy=[]
    sell=[]
    strong_buy=[]
    strong_sell=[]
    recommanded_list=[]
    

    #Bu yöntem en son 100 kripto para birimini listeler
    #filtering them by taking only the positive changes in 1h, 24h, 7d, +Vol_24h
    def get_marketCap():
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        parameters = {
        'start':'1',
        'limit':'100', # you can change this value to get bigger list, but it will effect raise the processing time around 2 min with each 100
        'convert':'USDT'#bridge coin (btcusdt) u can change it to BUSD or any bridge
        }
        headers = {
        'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': '328709da-cc4a-4fdf-8566-8c3d25d3e677',
        }

        session = Session()
        session.headers.update(headers)

        try:
            changes={}
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            
            with st.spinner("Yükseliş ve düşüş trendi gösterenler listeleniyor"):
                
                for d in data.keys():
                    if d=="data":
                        for i in data[d]:
                            ticker=i["symbol"]
                            Crypto_analysis.all.append(ticker)
                            proc_1h = i["quote"]["USDT"]["percent_change_1h"]
                            proc_24h= i["quote"]["USDT"]["percent_change_24h"]
                            proc_7d = i["quote"]["USDT"]["percent_change_7d"]
                            vol_ch24h=i["quote"]["USDT"]["volume_change_24h"]
                            changes[ticker] = [proc_1h,proc_24h ,proc_7d, vol_ch24h]
            
            Crypto_analysis.recommanded_list = [coin for coin in changes.keys() if changes[coin][0] and changes[coin][1]and changes[coin][2]and changes[coin][3]> 0] 
            
        except: 
            pass 
        st.success("İşlem tamam")
    
    def get_analysis_mma(ticker):
        try:
            ticker_summery = TA_Handler(
                symbol=ticker+"USDT",
                screener="crypto",
                exchange="binance",
                interval=Crypto_analysis.interval
            )
            
            rec = ticker_summery.get_analysis().moving_averages["RECOMMENDATION"]

            if rec == "SELL": Crypto_analysis.sell.append(ticker)
            if rec == "STRONG_SELL": Crypto_analysis.strong_sell.append(ticker)
            if rec == "BUY": Crypto_analysis.buy.append(ticker)
            if rec == "STRONG_BUY": Crypto_analysis.strong_buy.append(ticker)

        except:
            pass
        
    def get_analysis_osc(ticker):
        try:
            ticker_summery = TA_Handler(
                symbol=ticker+"USDT",
                screener="crypto",  
                exchange="binance", 
                interval=Crypto_analysis.interval 
            )
            Crypto_analysis.osc_coins[ticker] = ticker_summery.get_analysis().oscillators["RECOMMENDATION"]          
            
        except: 
            pass
       
    def do_draw_sidebar():

        # setup the screen for streamlit to be wide
        
        st.sidebar.header("Kripto analiz")
        Crypto_analysis.interval = st.sidebar.radio("Zaman aralığı",(
            "1 dakika", 
            "5 dakika",
            "15 dakika",
            "1 saat",
            "4 saat",
            "1 gün",
            "1 hafta",
            "1 ay"),2)

    def do_draw_body():
        
        st.header("AL/SAT LİSTESİ")
        col1, col2,col3,col4= st.columns(4)
   
        col1.success("Güçlü Al")
        col2.success("Al")
        col3.error("Sat")
        col4.error("Güçlü Sat")
        
        col1.table(list(Crypto_analysis.strong_buy))
        col2.table(list(Crypto_analysis.buy))
        col3.table(list(Crypto_analysis.sell))
        col4.table(list(Crypto_analysis.strong_sell))
    
    def do_analysis():
        with concurrent.futures.ProcessPoolExecutor() as executor:
            with st.spinner('Tüm kriptolar için OSC analizi yapılıyor...'):
                futures = [executor.submit(Crypto_analysis.get_analysis_osc(ticker),) for ticker in Crypto_analysis.all]
            st.success("İşlem tamam")
            with st.spinner('OSC analizi yapılan tüm kriptolar üzerinde MM analizi yapılıyor...'):
                futures = [executor.submit(Crypto_analysis.get_analysis_mma(ticker),) for ticker in Crypto_analysis.osc_coins.keys()]
            st.success("İşlem tamam")
def main():
    Crypto_analysis.do_draw_sidebar()
    Crypto_analysis.get_marketCap()
    Crypto_analysis.do_analysis()    
    Crypto_analysis.do_draw_body()
        
if __name__ == '__main__':
    start=datetime.now()
    main()
    st.write("Üretilme süresi",datetime.now()-start)
