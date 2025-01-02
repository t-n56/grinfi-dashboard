import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Industry-specific risk data generator
def generate_industry_data():
    industries = ['DeFi', 'Energy', 'Finance', 'Defense']
    countries = px.data.gapminder().country.unique()
    
    data = []
    for industry in industries:
        for country in countries:
            data.append({
                'country': country,
                'industry': industry,
                'political_risk': np.random.uniform(3, 9),
                'economic_risk': np.random.uniform(4, 8),
                'cyber_risk': np.random.uniform(5, 9),
                'environmental_risk': np.random.uniform(4, 9),
                'regulatory_risk': np.random.uniform(4, 9),
                'industry_specific_risk': np.random.uniform(5, 9),
                'last_updated': datetime.now() - timedelta(minutes=np.random.randint(0, 60))
            })
    return pd.DataFrame(data)

# Page config
st.set_page_config(layout="wide", page_title="Grinfi Industry Risk Monitor", page_icon="🛡️")

# Enhanced sidebar with industry filters
with st.sidebar:
    st.title("Industry Risk Monitor")
    
    # Industry selector
    selected_industry = st.selectbox(
        "Industry Focus",
        ["DeFi", "Energy", "Finance", "Defense"],
        help="Select industry for detailed analysis"
    )
    
    # Risk type selector
    risk_type = st.selectbox(
        "Risk Type",
        ["Political", "Economic", "Cyber", "Environmental", "Regulatory", "Industry Specific"]
    )
    
    # Industry-specific filters
    st.subheader(f"{selected_industry} Specific Filters")
    
    if selected_industry == "DeFi":
        st.multiselect("Protocol Type", ["DEX", "Lending", "Yield", "Bridge"])
        st.slider("TVL Range ($M)", 0, 1000, (100, 500))
        
    elif selected_industry == "Energy":
        st.multiselect("Energy Type", ["Renewable", "Nuclear", "Fossil Fuels"])
        st.slider("Carbon Impact", 0, 100, 50)
        
    elif selected_industry == "Finance":
        st.multiselect("Institution Type", ["Banks", "Insurance", "Investment"])
        st.slider("Market Cap ($B)", 0, 1000, (50, 200))
        
    elif selected_industry == "Defense":
        st.multiselect("Sector", ["Cybersecurity", "Aerospace", "Maritime"])
        st.slider("Contract Value ($M)", 0, 5000, (100, 1000))

# Main content
st.title(f"🎯 {selected_industry} Industry Risk Intelligence")

# Generate industry-specific data
industry_data = generate_industry_data()
filtered_data = industry_data[industry_data['industry'] == selected_industry]

# Industry-specific metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_risk = filtered_data[f"{risk_type.lower()}_risk"].mean()
    st.metric(f"Average {risk_type} Risk", f"{avg_risk:.1f}", f"{np.random.uniform(-0.5, 0.5):.1f}")

with col2:
    if selected_industry == "DeFi":
        st.metric("Total TVL", "$1.2B", "-2.3%")
    elif selected_industry == "Energy":
        st.metric("Energy Output", "2.4 GW", "+1.2%")
    elif selected_industry == "Finance":
        st.metric("Market Activity", "$3.4T", "+0.8%")
    elif selected_industry == "Defense":
        st.metric("Contract Volume", "$2.1B", "+5.2%")

with col3:
    high_risk = len(filtered_data[filtered_data[f"{risk_type.lower()}_risk"] > 7])
    st.metric("High Risk Regions", high_risk, f"+{np.random.randint(1,3)}")

with col4:
    st.metric("Risk Trend", "Stable", "↔")

# Industry-specific map
fig = go.Figure(data=go.Choropleth(
    locations=filtered_data['country'],
    locationmode='country names',
    z=filtered_data[f"{risk_type.lower()}_risk"],
    colorscale='RdYlGn_r',
    marker_line_color='darkgray',
    marker_line_width=0.5,
    colorbar_title=f'{risk_type} Risk Level'
))

fig.update_layout(
    title=f'Global {selected_industry} {risk_type} Risk Levels',
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# Industry-specific insights
st.subheader(f"{selected_industry} Specific Insights")

# Create tabs for different analyses
tab1, tab2, tab3 = st.tabs(["Risk Analysis", "Trends", "Recommendations"])

with tab1:
    # Radar chart for risk types
    categories = ['Political', 'Economic', 'Cyber', 'Environmental', 'Regulatory']
    values = [filtered_data[f"{cat.lower()}_risk"].mean() for cat in categories]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself'
    ))
    fig.update_layout(title=f"{selected_industry} Risk Profile")
    st.plotly_chart(fig)

with tab2:
    # Trend line for selected risk type
    dates = pd.date_range(start='2024-01-01', periods=30)
    trend_data = pd.DataFrame({
        'date': dates,
        'risk_score': np.cumsum(np.random.normal(0, 0.1, 30)) + 7
    })
    fig = px.line(trend_data, x='date', y='risk_score', title=f"{risk_type} Risk Trend")
    st.plotly_chart(fig)

with tab3:
    # Industry-specific recommendations
    if selected_industry == "DeFi":
        st.info("• Implement additional smart contract audits\n• Enhance liquidity monitoring\n• Update security protocols")
    elif selected_industry == "Energy":
        st.info("• Review environmental compliance\n• Assess grid stability\n• Update emergency response plans")
    elif selected_industry == "Finance":
        st.info("• Strengthen fraud detection\n• Update compliance frameworks\n• Enhance cyber security")
    elif selected_industry == "Defense":
        st.info("• Review supply chain security\n• Enhance data protection\n• Update crisis response protocols")
