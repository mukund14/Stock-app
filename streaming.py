#!/usr/bin/env python
# coding: utf-8


import newsapi
from newsapi import NewsApiClient

api_key='0ce8b6189282441e91727a812dc0f110'
newsapi = NewsApiClient(api_key=api_key)
from pandas.io.json import json_normalize
import pandas as pd
#pd.set_option('display.max_colwidth', -1)
import pprint as pp
import requests
from bs4 import BeautifulSoup

import numpy as np
from fuzzywuzzy import fuzz



import yfinance as yf
import streamlit as st
from yahoo_fin import stock_info as si
import re 
import pandas as pd
import plotly.express as px
import datetime
from datetime import datetime, timedelta

table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
df=table[0]
newdf=df[["Symbol","Security"]]
dic=newdf.set_index('Symbol')['Security'].to_dict()



def date(base):
    date_list=[]
    yr=datetime.today().year
    if (yr%400)==0 or ((yr%100!=0) and (yr%4==0)):
        numdays=366
        date_list.append([base - timedelta(days=x) for x in range(366)])
    else:
        numdays=365
        date_list.append([base - timedelta(days=x) for x in range(365)])
    newlist=[]
    for i in date_list:
        for j in sorted(i):
            newlist.append(j)
    return newlist

def last_30(base):

    date_list=[base - timedelta(days=x) for x in range(1)]
    #newlist=[]
    #for i in sorted(date_list):
    #    newlist.append(j)
    return sorted(date_list)


def from_dt(x):
    from_dt=[]
    for i in range(len(x)):
        from_dt.append(last_30(datetime.today())[i-1].date())
        #to_dt=date(datetime.today())[i+1].date()
    return from_dt
        
def to_dt(x):
    to_dt=[]
    for i in range(len(x)):
        #from_dt=date(datetime.today())[i].date()
        to_dt.append(last_30(datetime.today())[i].date())
    return to_dt
from_list=from_dt(last_30(datetime.today()))
to_list=to_dt(last_30(datetime.today()))

def make_clickable(link):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = link.split('=')[1]
    return f'<a target="_blank" href="{link}">{text}</a>'


def text_from_urls(query):
    newd={}
    for (from_dt,to_dt) in zip(from_list,to_list):
        all_articles = newsapi.get_everything(q=query,language='en',sort_by='relevancy', page_size=1,page=1,   from_param=from_dt,to=to_dt)
        d=json_normalize(all_articles['articles'])
        newdf=d[["url","source.name","title","content"]]
        
        dic=newdf.set_index(["source.name","title","content"])["url"].to_dict()
        #print(dic)
        for (k,v) in dic.items():
            #print(str(k[0])+str(k[1][5:10]))
            page = requests.get(v)
            html = page.content
            soup = BeautifulSoup(html, "lxml")
            text = soup.get_text()
            d2=soup.find_all("p")
            #for a in d2:
            newd[k]=re.sub(r'<.+?>',r'',str(d2)) 
    return newdf


st.write("""
# Stock shop
""")

nasdaq=pd.read_csv('nasdaqlisted.txt',sep='|')
nasdaq.head(3)
nasdaq=nasdaq[['Symbol','Security Name']]
other=pd.read_csv('otherlisted.txt',sep='|')
other=other[['ACT Symbol','Security Name']]
other=other.rename(columns={'ACT Symbol': 'Symbol'})
us_stocks=nasdaq.append(other)
stocks_dic=us_stocks.set_index('Symbol')['Security Name'].to_dict()


#def tick():
#    user_input = st.text_input("Enter stock symbol:", 'AAPL')
    
#    return user_input.upper()

tickerSymbol = str(st.text_input("Enter stock symbol:", 'AAPL'))
#get data on this ticker
for (k,v) in stocks_dic.items():
    if (tickerSymbol.upper()==k):
        tickerData = yf.Ticker(k)
        
        st.write("**"+"Current Stock Price of "+str(tickerData.get_info()['longName'])+" is: "+str(np.round(si.get_live_price(tickerSymbol),2))+"**")
        st.write("**"+"Here's the complete Closing Price trend for this month: "+"**"+str(tickerData.get_info()['longName']))

        def monthly_stock_trend_complete(tickerSymbol):
            d=pd.DataFrame()
            d=d.append(yf.Ticker(tickerSymbol).history(interval='1d').reset_index())
            fig = px.line(d, x="Date", y="Close",
                              labels={'Close':'Closing Stock Price'}, 
                              template='plotly_dark',
                             color_discrete_sequence=[ "aqua"],
                              title="Closing Stock Price for the Current Month for "+str(tickerData.get_info()['longName'])
                             )
            return st.plotly_chart(fig)



        monthly_stock_trend_complete(tickerSymbol)


        st.write("**Here's the complete Closing Price trend for this year: "+"**"+str(tickerData.get_info()['longName']))


        def yearly_stock_trend_complete(tickerSymbol):
            d=pd.DataFrame()
            d=d.append(yf.Ticker(tickerSymbol).history(period='1y',interval='1d').reset_index())
            d=d.reset_index()
            d['month'] = pd.DatetimeIndex(d['Date']).month
            d['years'] = pd.DatetimeIndex(d['Date']).year
            d['month']=d['month'].map({1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'})
            #d=d.sort_values(by='years',ascending=False,inplace=True)
            fig = px.line(d, x="Date", y="Close",
                              labels={'Close':'Closing Stock Price'}, 
                              template='plotly_dark',
                             color_discrete_sequence=[ "aqua"],
                              title="Closing Stock Price for the Current Year for "+str(tickerData.get_info()['longName'])
                             )
            return st.plotly_chart(fig)


        yearly_stock_trend_complete(tickerSymbol)

        st.write("\n\n**Here's the complete Closing Price trend for these  5 years: \n"+str(tickerData.get_info()['longName'])+"**")


        def stock_trend_complete(tickerSymbol):
            d=pd.DataFrame()
            d=d.append(yf.Ticker(tickerSymbol).history(period='5y',interval='1d').reset_index())
            fig = px.line(d, x="Date", y="Close",
                              labels={'Close':'Closing Stock Price'}, 
                              template='plotly_dark',
                             color_discrete_sequence=[ "aqua"],
                              title="Closing Stock Price for the Last 5 years for "+str(tickerData.get_info()['longName']))
            return st.write(fig)


        stock_trend_complete(tickerSymbol)
        import altair as alt
        #c = alt.Chart(df).mark_circle()

        #st.write("Dividends of "+str(tickerData.get_info()['longName']))
        df=tickerData.dividends.reset_index()


        df2=tickerData.get_recommendations().reset_index()

        df2['month'] = pd.DatetimeIndex(df2['Date']).month
        df2['year'] = pd.DatetimeIndex(df2['Date']).year

        df2['month']=df2['month'].map({1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'})
        d4=pd.DataFrame(df2.groupby(['year','month','To Grade'])['Firm'].count())
        d4=d4.reset_index()
        d4.rename(columns={'To Grade':'verdict','Firm':'count'},inplace=True)
        moonth= d4['month'].values.tolist()
        import plotly.graph_objects as go
        d3=d4[d4['verdict'].isin(['Buy','Hold','Outperform','Sell'])]
        #fig = go.Figure([go.Bar(data=d4,x='month', y='count')])
        fig=px.bar(d3,x='month',y='count',color='verdict',animation_frame='year',height=400,range_y=[0,30],template='plotly_dark',labels={'count':'Number of Analysts opinions'},barmode='relative',text='count',title="Analysts Recommendations in the Current Year ")
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 2000
        fig.update_yaxes(automargin=True)
        fig.update_layout(autosize=True)
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        
        
        st.write("Analyst recommend this")
        st.plotly_chart(fig)
        
    


        st.markdown("**"+"Related news"+"**")
        for (from_dt,to_dt) in zip(from_list,to_list):
            all_articles = newsapi.get_everything(q=str(tickerSymbol),language='en',sort_by='relevancy', page_size=3,page=1,   from_param=from_dt,to=to_dt)
            newdf=json_normalize(all_articles['articles'])
            #newdf=d[["url","source.name","title","content"]]
            st.write("***"+newdf['title'].values[0]+"***")
            st.write(newdf['content'].values[0]+"\n\n"+"You can find more about it here: "+newdf['url'].values[0]+"\n")
           # st.write("***"+"2] "+newdf['title'].values[1]+"***")
            
            #st.write(newdf['content'].values[1]+"\n\n"+"You can find more about it here: "+newdf['url'].values[1]+"\n")
            
            #st.write("***"+"3] "+newdf['title'].values[2]+"***")
            #st.write(str(newdf['content'].values[2])+"\n\n"+"You can find more about it here: "+str(newdf['url'].values[2])+"\n")

    else:
        print("Enter the stock symbol")







