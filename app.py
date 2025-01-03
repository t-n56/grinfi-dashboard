import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pandas_datareader.data as web  # Replaced yfinance
from datetime import datetime, timedelta
import requests
import wbgapi as wb
from alpha_vantage.timeseries import TimeSeries
from newsapi import NewsApiClient
from forex_python.converter import CurrencyRates
from countryinfo import CountryInfo
import asyncio
import aiohttp
from pytrends.request import TrendReq
import feedparser
import ccxt
import time

# Industry-specific metrics and data sources
INDUSTRY_FOCUS = {
    "DeFi": {
        "risk_factors": [
            "Smart Contract Vulnerabilities",
            "Protocol Security",
            "Liquidity Risk",
            "Regulatory Changes",
            "Market Manipulation",
            "Oracle Failures",
            "Network Congestion",
            "Governance Risks"
        ],
        "metrics": {
            "TVL": "Total Value Locked",
            "Protocol_Revenue": "Daily Revenue",
            "User_Activity": "Daily Active Users",
            "Gas_Costs": "Transaction Costs",
            "Hack_Events": "Security Incidents",
            "APY": "Average Yield",
            "Liquidity_Depth": "Market Depth",
            "Governance_Participation": "Voter Turnout"
        },
        "data_sources": [
            "CoinGecko API",
            "DeFi Pulse Index",
            "Ethereum Network Data",
            "DeFi Llama",
            "Dune Analytics",
            "The Graph Protocol"
        ]
    },
    "Energy": {
        "risk_factors": [
            "Environmental Regulations",
            "Resource Depletion",
            "Geopolitical Disruptions",
            "Infrastructure Vulnerability",
            "Price Volatility",
            "Supply Chain Risk",
            "Climate Policy Changes",
            "Technology Disruption"
        ],
        "metrics": {
            "Production": "Daily Production Rates",
            "Price_Volatility": "Price Change %",
            "Environmental_Impact": "Carbon Emissions",
            "Infrastructure_Status": "Facility Status",
            "Supply_Chain": "Supply Chain Disruptions",
            "Renewable_Mix": "Renewable Energy %",
            "Grid_Stability": "Grid Reliability",
            "Storage_Levels": "Energy Storage"
        },
        "data_sources": [
            "EIA Data",
            "World Bank Energy",
            "IEA Statistics",
            "EPA Reports",
            "Bloomberg NEF",
            "S&P Global Platts"
        ]
    },
    "Defense": {
        "risk_factors": [
            "Geopolitical Tensions",
            "Cyber Warfare",
            "Supply Chain Security",
            "Technology Obsolescence",
            "Regulatory Compliance",
            "Personnel Security",
            "Information Warfare",
            "Alliance Stability"
        ],
        "metrics": {
            "Threat_Level": "Global Threat Index",
            "Cyber_Incidents": "Security Breaches",
            "Supply_Chain": "Supply Chain Risk Score",
            "Tech_Readiness": "Technology Readiness Level",
            "Personnel_Risk": "Security Clearance Status",
            "Defense_Spending": "Military Expenditure",
            "R&D_Investment": "Research Investment",
            "Operational_Readiness": "Force Readiness"
        },
        "data_sources": [
            "Defense Industry Reports",
            "Military Spending Data",
            "Cyber Threat Intelligence",
            "Global Conflict Database",
            "NATO Statistics",
            "SIPRI Database"
        ]
    }
}

class RealTimeDataValidator:
    def __init__(self):
        self.sources = {
            'World Bank': wb.data,
            'Alpha Vantage': TimeSeries(key='YOUR_AV_KEY'),
            'Market Data': web,  # Changed from yfinance to pandas_datareader
            'IMF': 'IMF_API_KEY',
            'Reuters': 'REUTERS_API_KEY',
            'Bloomberg': 'BLOOMBERG_API_KEY',
            'CoinGecko': 'COINGECKO_API_KEY',
            'DeFi Pulse': 'DEFIPULSE_API_KEY'
        }
        self.exchange = ccxt.binance()
        self.pytrends = TrendReq()
        self.last_update = {}
        self.update_interval = 60
        self.confidence_threshold = 0.7

    async def get_cross_validated_data(self, metric_type, identifier):
        """Get real-time data from multiple sources and cross-validate"""
        data_points = {}
        async with aiohttp.ClientSession() as session:
            tasks = []
            for source_name, source in self.sources.items():
                tasks.append(self.fetch_data(session, source_name, metric_type, identifier))
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for source_name, result in zip(self.sources.keys(), results):
                if not isinstance(result, Exception):
                    data_points[source_name] = result

        validated_data = self.cross_validate_data_points(data_points)
        return validated_data

    def cross_validate_data_points(self, data_points):
        """Cross-validate data from different sources with enhanced validation"""
        if not data_points:
            return None

        values = [v for v in data_points.values() if v is not None]
        if not values:
            return None

        median = np.median(values)
        std = np.std(values)

        # Enhanced validation with weighted confidence
        validated_points = {}
        for source, value in data_points.items():
            if value is not None:
                z_score = abs((value - median) / std) if std > 0 else 0
                if z_score <= 2:  # Within 2 standard deviations
                    source_weight = self.get_source_weight(source)
                    validated_points[source] = {
                        'value': value,
                        'weight': source_weight,
                        'z_score': z_score
                    }

        if not validated_points:
            return None

        # Calculate weighted average and confidence
        total_weight = sum(point['weight'] for point in validated_points.values())
        weighted_value = sum(point['value'] * point['weight'] 
                           for point in validated_points.values()) / total_weight
        
        confidence = (len(validated_points) / len(data_points)) * \
                    (1 - np.mean([point['z_score'] for point in validated_points.values()]) / 2)

        return {
            'value': weighted_value,
            'confidence': confidence,
            'sources': list(validated_points.keys()),
            'timestamp': datetime.now()
        }

    def get_source_weight(self, source_name):
        """Get weight for each data source based on reliability"""
        weights = {
            'World Bank': 1.0,
            'Bloomberg': 0.9,
            'Reuters': 0.9,
            'Market Data': 0.8,
            'IMF': 0.9,
            'Alpha Vantage': 0.8,
            'CoinGecko': 0.7,
            'DeFi Pulse': 0.7
        }
        return weights.get(source_name, 0.5)

    async def fetch_market_data(self, symbol):
        """Fetch market data using pandas_datareader instead of yfinance"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            df = web.DataReader(symbol, 'yahoo', start_date, end_date)
            return df['Adj Close'][-1]
        except Exception as e:
            st.error(f"Error fetching market data: {str(e)}")
            return None

def create_global_risk_map():
    """Create enhanced interactive global risk map"""
    # Get comprehensive World Bank indicators
    indicators = {
        'PV.EST': 'Political Stability',
        'CC.EST': 'Control of Corruption',
        'RQ.EST': 'Regulatory Quality',
        'RL.EST': 'Rule of Law',
        'GE.EST': 'Government Effectiveness',
        'VA.EST': 'Voice and Accountability'
    }
    
    # Get data for all indicators
    wb_data = {}
    for code in indicators.keys():
        wb_data[code] = wb.data.DataFrame(code, time=range(2020, 2024), labels=True)
    
    # Create enhanced choropleth map
    fig = px.choropleth(
        wb_data['PV.EST'],
        locations=wb_data['PV.EST'].index.get_level_values(0),
        locationmode='ISO-3',
        color='value',
        hover_name=wb_data['PV.EST'].index.get_level_values(0),
        color_continuous_scale='RdYlGn_r',
        title='Global Risk Assessment',
        labels={'value': 'Risk Score'},
        animation_frame=wb_data['PV.EST'].index.get_level_values(1),
        height=800
    )
    
    # Enhanced hover information
    hover_template = "<b>%{hovertext}</b><br><br>"
    for code, name in indicators.items():
        hover_template += f"{name}: " + "%{customdata['" + code + "']:.2f}<br>"
    
    fig.update_traces(
        hovertemplate=hover_template + "<extra></extra>"
    )
    
    # Update layout for better visualization
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
            coastlinecolor='rgb(204, 204, 204)',
            showocean=True,
            oceancolor='rgb(230, 230, 230)'
        ),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig

# Page configuration
st.set_page_config(
    page_title="Grinfi ERM Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS styling
st.markdown("""
    <style>
    .main {
        background-color: #0A1F1C;
        color: #E6F3E6;
    }
    .headline {
        font-size: 3em;
        color: #00A36C;
        margin-bottom: 1em;
        text-align: center;
        font-weight: bold;
    }
    .subheadline {
        font-size: 1.8em;
        color: #E6F3E6;
        margin-bottom: 2em;
        text-align: center;
        line-height: 1.6;
    }
    .section-title {
        color: #00A36C;
        font-size: 2.2em;
        margin: 1.5em 0 1em 0;
        text-align: center;
    }
    .feature-card {
        background-color: #1A2C28;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #2C3C38;
        margin: 15px 0;
        transition: transform 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        border-color: #00A36C;
    }
    .metric-card {
        background-color: #1A2C28;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #00A36C;
    }
    .confidence-high { background-color: rgba(0, 255, 0, 0.1); }
    .confidence-medium { background-color: rgba(255, 255, 0, 0.1); }
    .confidence-low { background-color: rgba(255, 0, 0, 0.1); }
    .risk-high { color: #ff4444; }
    .risk-medium { color: #ffbb33; }
    .risk-low { color: #00C851; }
    .data-source { font-size: 0.8em; color: #888; }
    </style>
""", unsafe_allow_html=True)

# Initialize validator
data_validator = RealTimeDataValidator()

# Sidebar navigation
with st.sidebar:
    page = st.radio(
        "Navigation",
        ["Home", "Risk Analysis", "Industry Focus", "Trends", "Contact"]
    )
    
    if page == "Industry Focus":
        st.subheader("Industry Selection")
        selected_industry = st.selectbox(
            "Select Industry",
            list(INDUSTRY_FOCUS.keys())
        )
        
        if selected_industry:
            st.write("### Risk Factors")
            selected_risks = st.multiselect(
                "Select Risk Factors",
                INDUSTRY_FOCUS[selected_industry]["risk_factors"]
            )
            
            st.write("### Key Metrics")
            selected_metrics = st.multiselect(
                "Select Metrics",
                list(INDUSTRY_FOCUS[selected_industry]["metrics"].keys()),
                format_func=lambda x: INDUSTRY_FOCUS[selected_industry]["metrics"][x]
            )

# Main content based on selected page
if page == "Risk Analysis":
    st.title("Real-Time Risk Monitoring Dashboard")
    
    # Auto-refresh setup
    auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=True)
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 
                                       min_value=30, max_value=300, value=60)
    
    # Global Risk Map
    st.subheader("Global Risk Distribution")
    risk_map = create_global_risk_map()
    st.plotly_chart(risk_map, use_container_width=True)
    
    # Country Selection
    selected_country = st.selectbox(
        "Select Country for Detailed Analysis",
        wb.economy.list(labels=True)
    )
    
    if selected_country:
        # Create three columns for metrics
        col1, col2, col3 = st.columns(3)
        
        # Real-time metrics container
        metrics_container = st.container()
        
        while auto_refresh:
            with metrics_container:
                # Get cross-validated real-time data
                async def update_metrics():
                    political_risk = await data_validator.get_cross_validated_data(
                        'political_risk', selected_country)
                    economic_risk = await data_validator.get_cross_validated_data(
                        'economic_risk', selected_country)
                    market_risk = await data_validator.get_cross_validated_data(
                        'market_risk', selected_country)
                    
                    return political_risk, economic_risk, market_risk
                
                # Update metrics
                political_risk, economic_risk, market_risk = asyncio.run(update_metrics())
                
                # Display metrics with confidence levels
                with col1:
                    if political_risk:
                        confidence_class = (
                            'confidence-high' if political_risk['confidence'] > 0.8
                            else 'confidence-medium' if political_risk['confidence'] > 0.6
                            else 'confidence-low'
                        )
                        st.markdown(f"""
                            <div class="{confidence_class}">
                                <h3>Political Risk Score</h3>
                                <p class="risk-{'high' if political_risk['value'] > 7 
                                              else 'medium' if political_risk['value'] > 4 
                                              else 'low'}">
                                    {political_risk['value']:.2f}
                                </p>
                                <p>Confidence: {political_risk['confidence']:.1%}</p>
                                <p class="data-source">Sources: {', '.join(political_risk['sources'])}</p>
                            </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    if economic_risk:
                        confidence_class = (
                            'confidence-high' if economic_risk['confidence'] > 0.8
                            else 'confidence-medium' if economic_risk['confidence'] > 0.6
                            else 'confidence-low'
                        )
                        st.markdown(f"""
                            <div class="{confidence_class}">
                                <h3>Economic Risk Score</h3>
                                <p class="risk-{'high' if economic_risk['value'] > 7 
                                              else 'medium' if economic_risk['value'] > 4 
                                              else 'low'}">
                                    {economic_risk['value']:.2f}
                                </p>
                                <p>Confidence: {economic_risk['confidence']:.1%}</p>
                                <p class="data-source">Sources: {', '.join(economic_risk['sources'])}</p>
                            </div>
                        """, unsafe_allow_html=True)
                
                with col3:
                    if market_risk:
                        confidence_class = (
                            'confidence-high' if market_risk['confidence'] > 0.8
                            else 'confidence-medium' if market_risk['confidence'] > 0.6
                            else 'confidence-low'
                        )
                        st.markdown(f"""
                            <div class="{confidence_class}">
                                <h3>Market Risk Score</h3>
                                <p class="risk-{'high' if market_risk['value'] > 7 
                                              else 'medium' if market_risk['value'] > 4 
                                              else 'low'}">
                                    {market_risk['value']:.2f}
                                </p>
                                <p>Confidence: {market_risk['confidence']:.1%}</p>
                                <p class="data-source">Sources: {', '.join(market_risk['sources'])}</p>
                            </div>
                        """, unsafe_allow_html=True)
                
                # Update timestamp
                st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Wait for next refresh
            time.sleep(refresh_interval)

elif page == "Industry Focus":
    st.title(f"{selected_industry} Industry Analysis")
    
    if selected_industry == "DeFi":
        # DeFi-specific metrics and visualizations
        defi_data = {
            'tvl': np.random.uniform(1000000, 10000000),
            'protocol_revenue': np.random.uniform(10000, 100000),
            'user_activity': np.random.randint(1000, 10000),
            'security_incidents': np.random.randint(0, 10)
        }
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Value Locked", f"${defi_data['tvl']:,.2f}")
        with col2:
            st.metric("Protocol Revenue", f"${defi_data['protocol_revenue']:,.2f}")
        with col3:
            st.metric("Active Users", f"{defi_data['user_activity']:,}")
        
        # DeFi risk visualization
        st.subheader("Risk Analysis")
        fig = go.Figure(data=[
            go.Bar(name='Security Incidents', x=['Last 30 Days'], y=[defi_data['security_incidents']]),
            go.Bar(name='Protocol Revenue', x=['Last 30 Days'], y=[defi_data['protocol_revenue']])
        ])
        st.plotly_chart(fig)
        
    elif selected_industry == "Energy":
        # Energy-specific metrics and visualizations
        energy_data = {
            'production_rates': np.random.uniform(1000, 5000),
            'environmental_impact': np.random.uniform(0, 100),
            'supply_chain': np.random.uniform(0, 10)
        }
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Production Rate", f"{energy_data['production_rates']:,.2f} MWh")
        with col2:
            st.metric("Environmental Impact", f"{energy_data['environmental_impact']:.1f}%")
        with col3:
            st.metric("Supply Chain Risk", f"{energy_data['supply_chain']:.1f}/10")
        
        # Energy risk visualization
        st.subheader("Risk Analysis")
        fig = go.Figure(data=[
            go.Scatter(x=['Production', 'Environment', 'Supply Chain'], 
                      y=[energy_data['production_rates'], 
                         energy_data['environmental_impact'], 
                         energy_data['supply_chain']])
        ])
        st.plotly_chart(fig)
        
    elif selected_industry == "Defense":
        # Defense-specific metrics and visualizations
        defense_data = {
            'threat_levels': np.random.uniform(0, 10),
            'cyber_incidents': np.random.randint(0, 100),
            'supply_chain': np.random.uniform(0, 10)
        }
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Threat Level", f"{defense_data['threat_levels']:.1f}/10")
        with col2:
            st.metric("Cyber Incidents", str(defense_data['cyber_incidents']))
        with col3:
            st.metric("Supply Chain Risk", f"{defense_data['supply_chain']:.1f}/10")
        
        # Defense risk visualization
        st.subheader("Risk Analysis")
        fig = go.Figure(data=[
            go.Radar(
                r=[defense_data['threat_levels'], 
                   defense_data['cyber_incidents']/10, 
                   defense_data['supply_chain']],
                theta=['Threats', 'Cyber', 'Supply Chain']
            )
        ])
        st.plotly_chart(fig)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <p style='color: #00A36C; font-size: 1.2em;'>Grinfi Consulting | Driving Innovation in Risk Analysis</p>
        <p>Contact Us: info@grinfi.com | <a href="#" style='color: #00A36C;'>LinkedIn</a> | <a href="#" style='color: #00A36C;'>Twitter</a></p>
    </div>
""", unsafe_allow_html=True)
