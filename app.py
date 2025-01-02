import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Grinfi ERM Platform",
    page_icon="🛡️",
    layout="wide"
)

# Main content
st.title("🛡️ Grinfi ERM Platform")

# Create data
risk_data = pd.DataFrame({
    'Risk Type': ['Cyber', 'Financial', 'Operational', 'Regulatory'],
    'Score': [8.5, 6.2, 7.1, 5.9]
})

# Display metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Global Risk Score", "7.8", "-0.2")
with col2:
    st.metric("Active Alerts", "12", "3")
with col3:
    st.metric("Assets Monitored", "156", "5")

# Create chart
fig = px.bar(risk_data, 
             x='Risk Type', 
             y='Score',
             color='Score',
             color_continuous_scale='RdYlGn_r')
st.plotly_chart(fig, use_container_width=True)
risk_data = pd.DataFrame({
    'Risk Type': ['Cyber', 'Financial', 'Operational', 'Regulatory'],
    'Score': [8.5, 6.2, 7.1, 5.9]
})

fig = px.bar(risk_data, 
             x='Risk Type', 
             y='Score',
             color='Score',
             color_continuous_scale='RdYlGn_r')
st.plotly_chart(fig, use_container_width=True)

# Recent Alerts
st.subheader("Recent Alerts")
alerts = [
    {"severity": "High", "message": "Unusual network activity detected"},
    {"severity": "Medium", "message": "Policy update required"},
    {"severity": "Low", "message": "System maintenance scheduled"}
]

for alert in alerts:
    st.warning(f"{alert['severity']}: {alert['message']}")