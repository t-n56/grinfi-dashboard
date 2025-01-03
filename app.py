import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json

# Define country data directly in the code
COUNTRY_DATA = {
    'USA': {'name': 'United States', 'region': 'North America', 'iso3': 'USA'},
    'CAN': {'name': 'Canada', 'region': 'North America', 'iso3': 'CAN'},
    'MEX': {'name': 'Mexico', 'region': 'North America', 'iso3': 'MEX'},
    'GBR': {'name': 'United Kingdom', 'region': 'Europe', 'iso3': 'GBR'},
    'FRA': {'name': 'France', 'region': 'Europe', 'iso3': 'FRA'},
    'DEU': {'name': 'Germany', 'region': 'Europe', 'iso3': 'DEU'},
    'ITA': {'name': 'Italy', 'region': 'Europe', 'iso3': 'ITA'},
    'ESP': {'name': 'Spain', 'region': 'Europe', 'iso3': 'ESP'},
    'PRT': {'name': 'Portugal', 'region': 'Europe', 'iso3': 'PRT'},
    'CHE': {'name': 'Switzerland', 'region': 'Europe', 'iso3': 'CHE'},
    'AUT': {'name': 'Austria', 'region': 'Europe', 'iso3': 'AUT'},
    'BEL': {'name': 'Belgium', 'region': 'Europe', 'iso3': 'BEL'},
    'NLD': {'name': 'Netherlands', 'region': 'Europe', 'iso3': 'NLD'},
    'SWE': {'name': 'Sweden', 'region': 'Europe', 'iso3': 'SWE'},
    'NOR': {'name': 'Norway', 'region': 'Europe', 'iso3': 'NOR'},
    'DNK': {'name': 'Denmark', 'region': 'Europe', 'iso3': 'DNK'},
    'FIN': {'name': 'Finland', 'region': 'Europe', 'iso3': 'FIN'},
    'POL': {'name': 'Poland', 'region': 'Europe', 'iso3': 'POL'},
    'CHN': {'name': 'China', 'region': 'Asia', 'iso3': 'CHN'},
    'JPN': {'name': 'Japan', 'region': 'Asia', 'iso3': 'JPN'},
    'KOR': {'name': 'South Korea', 'region': 'Asia', 'iso3': 'KOR'},
    'IND': {'name': 'India', 'region': 'Asia', 'iso3': 'IND'},
    'IDN': {'name': 'Indonesia', 'region': 'Asia', 'iso3': 'IDN'},
    'MYS': {'name': 'Malaysia', 'region': 'Asia', 'iso3': 'MYS'},
    'SGP': {'name': 'Singapore', 'region': 'Asia', 'iso3': 'SGP'},
    'THA': {'name': 'Thailand', 'region': 'Asia', 'iso3': 'THA'},
    'VNM': {'name': 'Vietnam', 'region': 'Asia', 'iso3': 'VNM'},
    'AUS': {'name': 'Australia', 'region': 'Oceania', 'iso3': 'AUS'},
    'NZL': {'name': 'New Zealand', 'region': 'Oceania', 'iso3': 'NZL'},
    'BRA': {'name': 'Brazil', 'region': 'South America', 'iso3': 'BRA'},
    'ARG': {'name': 'Argentina', 'region': 'South America', 'iso3': 'ARG'},
    'CHL': {'name': 'Chile', 'region': 'South America', 'iso3': 'CHL'},
    'COL': {'name': 'Colombia', 'region': 'South America', 'iso3': 'COL'},
    'PER': {'name': 'Peru', 'region': 'South America', 'iso3': 'PER'},
    'ZAF': {'name': 'South Africa', 'region': 'Africa', 'iso3': 'ZAF'},
    'NGA': {'name': 'Nigeria', 'region': 'Africa', 'iso3': 'NGA'},
    'EGY': {'name': 'Egypt', 'region': 'Africa', 'iso3': 'EGY'},
    'MAR': {'name': 'Morocco', 'region': 'Africa', 'iso3': 'MAR'},
    'KEN': {'name': 'Kenya', 'region': 'Africa', 'iso3': 'KEN'},
    'SAU': {'name': 'Saudi Arabia', 'region': 'Middle East', 'iso3': 'SAU'},
    'ARE': {'name': 'United Arab Emirates', 'region': 'Middle East', 'iso3': 'ARE'},
    'ISR': {'name': 'Israel', 'region': 'Middle East', 'iso3': 'ISR'},
    'TUR': {'name': 'Turkey', 'region': 'Middle East', 'iso3': 'TUR'},
    'IRN': {'name': 'Iran', 'region': 'Middle East', 'iso3': 'IRN'}
}

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
        }
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
        }
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
        }
    }
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
            'region': True
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
                st.write(f"ISO Code: {country_data['iso3']}")
            
            with col2:
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
        <p>Contact Us: contact@grinficonsulting.com | <a href="#" style='color: #00A36C;'>LinkedIn</a> | <a href="#" style='color: #00A36C;'>Twitter</a></p>
    </div>
""", unsafe_allow_html=True)
