import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from countryinfo import CountryInfo
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

def get_all_countries():
    """Get data for all countries in the world"""
    try:
        countries_data = []
        all_countries = [
            'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda',
            'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain',
            'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan',
            'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria',
            'Burkina Faso', 'Burundi', 'Cabo Verde', 'Cambodia', 'Cameroon', 'Canada',
            'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros',
            'Congo', 'Costa Rica', 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic',
            'Democratic Republic of the Congo', 'Denmark', 'Djibouti', 'Dominica',
            'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea',
            'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia', 'Fiji', 'Finland', 'France',
            'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada',
            'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Honduras',
            'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland',
            'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya',
            'Kiribati', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho',
            'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Madagascar',
            'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands',
            'Mauritania', 'Mauritius', 'Mexico', 'Micronesia', 'Moldova', 'Monaco',
            'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia',
            'Nauru', 'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger',
            'Nigeria', 'North Korea', 'North Macedonia', 'Norway', 'Oman', 'Pakistan',
            'Palau', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru',
            'Philippines', 'Poland', 'Portugal', 'Qatar', 'Romania', 'Russia', 'Rwanda',
            'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines',
            'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal',
            'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia',
            'Solomon Islands', 'Somalia', 'South Africa', 'South Korea', 'South Sudan',
            'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria',
            'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Timor-Leste', 'Togo',
            'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu',
            'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States',
            'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City', 'Venezuela', 'Vietnam',
            'Yemen', 'Zambia', 'Zimbabwe'
        ]
        
        for country_name in all_countries:
            try:
                country = CountryInfo(country_name)
                country_data = {
                    'name': country_name,
                    'iso3': country.iso(3) if hasattr(country, 'iso') else 'N/A',
                    'region': country.region() if hasattr(country, 'region') else 'N/A',
                    'subregion': country.subregion() if hasattr(country, 'subregion') else 'N/A',
                    'capital': country.capital() if hasattr(country, 'capital') else 'N/A',
                    'population': country.population() if hasattr(country, 'population') else 0,
                    'area': country.area() if hasattr(country, 'area') else 0,
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
            except Exception as e:
                st.warning(f"Could not load data for {country_name}: {str(e)}")
                continue
        
        return pd.DataFrame(countries_data)
    except Exception as e:
        st.error(f"Error loading country data: {str(e)}")
        return pd.DataFrame()

def create_global_risk_map(df):
    """Create enhanced risk map with all countries"""
    fig = px.choropleth(
        df,
        locations='iso3',
        color='composite_risk',
        hover_name='name',
        hover_data={
            'political_risk': ':.2f',
            'economic_risk': ':.2f',
            'social_risk': ':.2f',
            'environmental_risk': ':.2f',
            'composite_risk': ':.2f',
            'population': ':,',
            'region': True,
            'subregion': True
        },
        color_continuous_scale='RdYlGn_r',
        title='Global Risk Assessment',
        height=800
    )
    
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

# Main content
if page == "Home":
    st.title("Welcome to Grinfi ERM Platform")
    st.write("Global Risk Management and Analysis")
    
elif page == "Risk Analysis":
    st.title("Real-Time Risk Monitoring Dashboard")
    
    # Load country data
    df_countries = get_all_countries()
    
    if not df_countries.empty:
        # Global Risk Map
        st.subheader("Global Risk Distribution")
        risk_map = create_global_risk_map(df_countries)
        st.plotly_chart(risk_map, use_container_width=True)
        
        # Country Selection
        selected_country = st.selectbox(
            "Select Country for Detailed Analysis",
            df_countries['name'].tolist()
        )
        
        if selected_country:
            country_data = df_countries[df_countries['name'] == selected_country].iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Political Risk",
                    f"{country_data['political_risk']:.2f}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    "Economic Risk",
                    f"{country_data['economic_risk']:.2f}",
                    delta=None
                )
            
            with col3:
                st.metric(
                    "Social Risk",
                    f"{country_data['social_risk']:.2f}",
                    delta=None
                )
            
            with col4:
                st.metric(
                    "Environmental Risk",
                    f"{country_data['environmental_risk']:.2f}",
                    delta=None
                )
            
            # Country Details
            st.subheader(f"Details for {selected_country}")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"Region: {country_data['region']}")
                st.write(f"Subregion: {country_data['subregion']}")
                st.write(f"Capital: {country_data['capital']}")
            
            with col2:
                st.write(f"Population: {country_data['population']:,}")
                st.write(f"Area: {country_data['area']:,} km²")
                st.write(f"Composite Risk Score: {country_data['composite_risk']:.2f}")

elif page == "Industry Focus":
    if selected_industry:
        st.title(f"{selected_industry} Industry Analysis")
        
        if selected_industry == "DeFi":
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
            
            st.subheader("Risk Analysis")
            fig = go.Figure(data=[
                go.Bar(name='Security Incidents', x=['Last 30 Days'], y=[defi_data['security_incidents']]),
                go.Bar(name='Protocol Revenue', x=['Last 30 Days'], y=[defi_data['protocol_revenue']])
            ])
            st.plotly_chart(fig)
            
        elif selected_industry == "Energy":
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
            
            st.subheader("Risk Analysis")
            fig = go.Figure(data=[
                go.Scatter(x=['Production', 'Environment', 'Supply Chain'], 
                          y=[energy_data['production_rates'], 
                             energy_data['environmental_impact'], 
                             energy_data['supply_chain']])
            ])
            st.plotly_chart(fig)
            
        elif selected_industry == "Defense":
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

elif page == "Trends":
    st.title("Global Risk Trends")
    st.write("Coming soon...")

elif page == "Contact":
    st.title("Contact Us")
    st.write("For more information, please reach out to us.")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <p style='color: #00A36C; font-size: 1.2em;'>Grinfi Consulting | Driving Innovation in Risk Analysis</p>
        <p>Contact Us: info@grinfi.com | <a href="#" style='color: #00A36C;'>LinkedIn</a> | <a href="#" style='color: #00A36C;'>Twitter</a></p>
    </div>
""", unsafe_allow_html=True)
