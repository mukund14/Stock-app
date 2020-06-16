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


#x = st.slider('x')  #  this is a widget

def tick():
    user_input = st.text_input("Enter stock symbol:", 'AAPL')
    
    return user_input.upper()

tickerSymbol = str(tick())
#get data on this ticker
tickerData = yf.Ticker(tickerSymbol)


newd={}
    
    #st.write(text_from_urls(tickerData.get_info()['longName']).to_html(escape=False, index=False), unsafe_allow_html=True)

#dic=func(tickerData.get_info()['longName'])
new=tickerSymbol


st.write("**"+"Current Stock Price of "+str(tickerSymbol)+" is: "+str(np.round(si.get_live_price(tickerSymbol,2))+"**"))
st.write("**"+"Here's the complete Closing Price trend for this month: "+"**"+str(tickerSymbol))

def monthly_stock_trend_complete(tickerSymbol):
    s=tickerSymbol
    d=pd.DataFrame()
    try:
        for (k,v) in dic.items():
            if re.compile(s.lower()).match(v.lower()):
                d=d.append(yf.Ticker(k).history(interval='1d').reset_index())
            elif re.compile(s.lower()).match(k.lower()):
                d=d.append(yf.Ticker(k).history(interval='1d').reset_index())
        fig = px.line(d, x="Date", y="Close",
                      labels={'Close':'Closing Stock Price'}, 
                      template='plotly_dark',
                     color_discrete_sequence=[ "aqua"],
                      title="Closing Stock Price for the Current Month for "+str(s)
                     )
        return st.plotly_chart(fig)
    except Exception as e: # work on python 3.x
        st.write(str(e)) 


monthly_stock_trend_complete(tickerSymbol)


st.write("\n\n**Here's the complete Closing Price trend for this year: \n\n"+str(tickerSymbol)+"**")


def yearly_stock_trend_complete(tickerSymbol):
    s=tickerSymbol
    d=pd.DataFrame()
    try:
        for (k,v) in dic.items():
            if re.compile(s.lower()).match(v.lower()):
                d=d.append(yf.Ticker(k).history(period='1y',interval='1d').reset_index())
            elif re.compile(s.lower()).match(k.lower()):
                d=d.append(yf.Ticker(k).history(period='1y',interval='1d').reset_index())
        fig = px.line(d, x="Date", y="Close",
                      labels={'Close':'Closing Stock Price'}, 
                      template='plotly_dark',
                     color_discrete_sequence=[ "aqua"],
                      title="Closing Stock Price for the Current Year for "+str(s)
                     )
        return st.plotly_chart(fig)
    except Exception as e: # work on python 3.x
        st.write(str(e))  

yearly_stock_trend_complete(tickerSymbol)

st.write("\n\n**Here's the complete Closing Price trend for these  5 years: \n"+str(tickerSymbol)+"**")


def stock_trend_complete(tickerSymbol):
    s=tickerSymbol
    d=pd.DataFrame()
    try:
        for (k,v) in dic.items():
            if re.compile(s.lower()).match(v.lower()):
                d=d.append(yf.Ticker(k).history(period='5y',interval='1d').reset_index())
            elif re.compile(s.lower()).match(k.lower()):
                d=d.append(yf.Ticker(k).history(period='5y',interval='1d').reset_index())
        fig = px.line(d, x="Date", y="Close",
                      labels={'Close':'Closing Stock Price'}, 
                      template='plotly_dark',
                     color_discrete_sequence=[ "aqua"],
                      title="Closing Stock Price for the Last 5 years for "+str(s)
                     )
        return st.write(fig)
    except Exception as e: # work on python 3.x
        st.write(str(e))  

stock_trend_complete(tickerSymbol)
import altair as alt
#c = alt.Chart(df).mark_circle()

st.write("Dividends of "+str(tickerSymbol))

st.write(tickerData.dividends.tail(3))
st.write("Analyst Recommendations of "+str(tickerSymbol))
st.write(tickerData.get_recommendations())
st.write("Calendar of "+str(tickerSymbol))

st.write(tickerData.calendar)

st.write("Major Holders of "+str(tickerSymbol))

st.write(tickerData.major_holders)

st.write("Actions of "+str(tickerSymbol))


st.write(tickerData.actions)


st.markdown("**"+"Related news"+"**")
for (from_dt,to_dt) in zip(from_list,to_list):
    all_articles = newsapi.get_everything(q=str(tickerData.get_info()['longName']),language='en',sort_by='relevancy', page_size=3,page=1,   from_param=from_dt,to=to_dt)
    d=json_normalize(all_articles['articles'])
    newdf=d[["url","source.name","title","content"]]
        
    e="""   dic=newdf.set_index(["source.name","title","content"])["url"].to_dict()
        #print(dic)
        for (k,v) in dic.items():
            #print(str(k[0])+str(k[1][5:10]))
            page = requests.get(v)
            html = page.content
            soup = BeautifulSoup(html, "lxml")
            text = soup.get_text()
            d2=soup.find_all("p")
            #for a in d2:
            newd[k]=re.sub(r'<.+?>',r'',str(d2)) """

    st.write("***"+""+newdf['title'].values[0]+"***")
    st.write("1] "+newdf['content'].values[0]+"\n\n"+"You can find more about it here: "+newdf['url'].values[0]+"\n")
    st.write("***"+""+newdf['title'].values[1]+"***")
    
    st.write("2] "+newdf['content'].values[1]+"\n\n"+"You can find more about it here: "+newdf['url'].values[1]+"\n")
    st.write("***"+""+newdf['title'].values[2]+"***")
    
    st.write("3] "+newdf['content'].values[2]+"\n\n"+"You can find more about it here: "+newdf['url'].values[2]+"\n")

#st.write(text_from_urls(new))

#get the historical prices for this ticker
tickerDf = tickerData.history(period='1d', start='2010-5-31', end='2020-5-31')
# Open	High	Low	Close	Volume	Dividends	Stock Splits






