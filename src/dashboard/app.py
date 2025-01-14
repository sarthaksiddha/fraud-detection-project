import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from typing import Dict, Any

class FraudDashboard:
    """Interactive dashboard for fraud detection monitoring."""
    
    def __init__(self, api_base_url: str):
        """Initialize dashboard with API endpoint.
        
        Args:
            api_base_url (str): Base URL for fraud detection API
        """
        self.api_base_url = api_base_url
        st.set_page_config(
            page_title="Fraud Detection Dashboard",
            page_icon="🔍",
            layout="wide"
        )
    
    def render_metrics(self, metrics: Dict[str, float]):
        """Render key metrics in columns."""
        cols = st.columns(4)
        
        with cols[0]:
            st.metric(
                "Total Transactions",
                f"{metrics['total_transactions']:,}",
                f"{metrics['transaction_change']}%"
            )
        
        with cols[1]:
            st.metric(
                "Fraud Alerts",
                f"{metrics['total_alerts']:,}",
                f"{metrics['alert_change']}%"
            )
    
    def render_dashboard(self):
        """Render complete dashboard."""
        st.title("Fraud Detection Dashboard")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs([
            "Transaction Trends",
            "Alert Map",
            "Alert Management"
        ])
        
        with tab1:
            # Fetch trend data
            trend_data = self.fetch_data("api/v1/trends")
            df_trend = pd.DataFrame(trend_data['trends'])
            self.render_transaction_trend(df_trend)

def main():
    dashboard = FraudDashboard("http://localhost:8000")
    dashboard.render_dashboard()

if __name__ == "__main__":
    main()