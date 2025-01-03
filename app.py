import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from alpha_vantage.timeseries import TimeSeries
from newsapi import NewsApiClient
from forex_python.converter import CurrencyRates
import asyncio
import aiohttp
from pytrends.request import TrendReq
import feedparser
import ccxt
import time
import json

# Define country data directly in the code
COUNTRY_DATA = {
    'USA': {'name': 'United States', 'region': 'North America', 'iso3': 'USA'},
    'GBR': {'name': 'United Kingdom', 'region': 'Europe', 'iso3': 'GBR'},
    'FRA': {'name': 'France', 'region': 'Europe', 'iso3': 'FRA'},
    'DEU': {'name': 'Germany', 'region': 'Europe', 'iso3': 'DEU'},
    'ITA': {'name': 'Italy', 'region': 'Europe', 'iso3': 'ITA'},
    'ESP': {'name': 'Spain', 'region': 'Europe', 'iso3': 'ESP'},
    'CHN': {'name': 'China', 'region': 'Asia', 'iso3': 'CHN'},
    'JPN': {'name': 'Japan', 'region': 'Asia', 'iso3': 'JPN'},
    'IND': {'name': 'India', 'region': 'Asia', 'iso3': 'IND'},
    'BRA': {'name': 'Brazil', 'region': 'South America', 'iso3': 'BRA'},
    # Add more countries as needed
}

def get_all_countries():
    """Get data for all countries"""
    try:
        countries_data = []
        for code, info in COUNTRY_DATA.items():
            country_data = {
                'name': info['name'],
                'iso3': info['iso3'],
                'region': info['region'],
                'political_risk': np.random.uniform(0, 1),
                'economic_risk': np.random.uniform(0, 1),
                'social_risk': np.random.uniform(0, 1),
                'environmental_risk': np.random.uniform(0, 1),
                'composite_risk': 0
            }
            
            country_data['composite_risk'] = np.mean([
                country_data['political_risk'],
                country_data['economic_risk'],
                country_data['social_risk'],
                country_data['environmental_risk']
            ])
            
            countries_data.append(country_data)
        
        return pd.DataFrame(countries_data)
    except Exception as e:
        st.error(f"Error loading country data: {str(e)}")
        return pd.DataFrame()
