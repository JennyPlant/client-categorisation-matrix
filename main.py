import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import io
from typing import Optional

# Configure page
st.set_page_config(
    page_title="Client Categorisation Matrix",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit branding
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Embedded demo data
DEMO_DATA = """Client_Name,Strategic_Importance_(1-5),Spend_Potential_(1-5),Relationship_Risk_(R/A/G),FY25_Revenue,%_of_Total_Revenue
Arctic Tours,1,2,R,200000,28%
Blackpool Tower,1,2,A,5000,1%
Crest Hotels,4,1,G,35000,5%
Dan Air,4,5,A,26500,4%
EasyJetter,5,4,G,30000,4%
Finland Tourist Board,1,4,A,60000,8%
Grange Hotel Group,3,3,R,45000,6%
Hotelfinance.com,4,2,A,92500,13%
Iceland Tours,5,1,R,69500,10%
Jupiter Travel Ltd,1,1,A,8500,1%
Kenyan Safari Group,2,2,A,16000,2%
Lapland Holidays,4,3,G,16000,2%
Monte Carlo Yachting Group,5,5,G,105000,15%"""

def load_demo_data() -> pd.DataFrame:
    """Load the embedded demo data."""
    return pd.read_csv(io.StringIO(DEMO_DATA))

def clean_percentage_column(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the percentage column by removing % symbol and converting to float."""
    df = df.copy()
    if '%_of_Total_Revenue' in df.columns:
        df['%_of_Total_Revenue'] = df['%_of_Total_Revenue'].astype(str).str.replace('%', '').astype(float)
    return df

def load_data_from_url(url: str) -> Optional[pd.DataFrame]:
    """Load data from a CSV URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        return clean_percentage_column(df)
    except Exception as e:
        st.error(f"Error loading data from URL: {str(e)}")
        return None

def load_data_from_file(uploaded_file) -> Optional[pd.DataFrame]:
    """Load data from an uploaded file."""
    try:
        df = pd.read_csv(uploaded_file)
        return clean_percentage_column(df)
    except Exception as e:
        st.error(f"Error loading data from file: {str(e)}")
        return None

def validate_data(df: pd.DataFrame) -> bool:
    """Validate that the dataframe has required columns."""
    required_columns = [
        'Client_Name',
        'Strategic_Importance_(1-5)',
        'Spend_Potential_(1-5)',
        'Relationship_Risk_(R/A/G)',
        'FY25_Revenue',
        '%_of_Total_Revenue'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
        st.info(f"Required columns: {', '.join(required_columns)}")
        return False
    
    return True

def create_scatter_plot(df: pd.DataFrame) -> go.Figure:
    """Create the client categorisation matrix scatter plot."""
    # Define color mapping for risk levels
    color_map = {'R': '#FF4444', 'A': '#FFA500', 'G': '#00AA00'}
    
    # Create the scatter plot with larger bubble sizes
    fig = px.scatter(
        df,
        x='Spend_Potential_(1-5)',
        y='Strategic_Importance_(1-5)',
        size='%_of_Total_Revenue',
        color='Relationship_Risk_(R/A/G)',
        color_discrete_map=color_map,
        size_max=60,  # Increased max size for larger bubbles
        hover_data={
            'Client_Name': True,
            'Strategic_Importance_(1-5)': True,
            'Spend_Potential_(1-5)': True,
            'Relationship_Risk_(R/A/G)': True,
            'FY25_Revenue': ':,.0f',
            '%_of_Total_Revenue': ':.1f%'
        },
        title="Client Categorisation Matrix",
        labels={
            'Spend_Potential_(1-5)': '',
            'Strategic_Importance_(1-5)': '',
            'Relationship_Risk_(R/A/G)': 'Relationship Risk'
        }
    )
    
    # Add quadrant background rectangles
    fig.add_shape(
        type="rect", x0=0.5, y0=3, x1=3, y1=5.5,
        fillcolor="lightgray", opacity=0.15, layer="below", line_width=0
    )
    fig.add_shape(
        type="rect", x0=3, y0=3, x1=5.5, y1=5.5,
        fillcolor="lightblue", opacity=0.15, layer="below", line_width=0
    )
    fig.add_shape(
        type="rect", x0=0.5, y0=0.5, x1=3, y1=3,
        fillcolor="lightyellow", opacity=0.15, layer="below", line_width=0
    )
    fig.add_shape(
        type="rect", x0=3, y0=0.5, x1=5.5, y1=3,
        fillcolor="lightgreen", opacity=0.15, layer="below", line_width=0
    )
    
    # Add quadrant labels
    fig.add_annotation(x=1.75, y=4.25, text="<b>Bronze</b>", showarrow=False, 
                      font=dict(size=16, color="gray"), bgcolor="white", opacity=0.8)
    fig.add_annotation(x=4.25, y=4.25, text="<b>Platinum</b>", showarrow=False, 
                      font=dict(size=16, color="darkblue"), bgcolor="white", opacity=0.8)
    fig.add_annotation(x=1.75, y=1.75, text="<b>Silver</b>", showarrow=False, 
                      font=dict(size=16, color="gray"), bgcolor="white", opacity=0.8)
    fig.add_annotation(x=4.25, y=1.75, text="<b>Gold</b>", showarrow=False, 
                      font=dict(size=16, color="darkgreen"), bgcolor="white", opacity=0.8)
    
    # Add reference lines (dividing quadrants)
    fig.add_vline(x=3, line_dash="solid", line_color="darkgray", line_width=2, opacity=0.7)
    fig.add_hline(y=3, line_dash="solid", line_color="darkgray", line_width=2, opacity=0.7)
    
    # Update layout with arrows and axis styling
    fig.update_layout(
        width=900,
        height=700,
        plot_bgcolor='white',
        xaxis=dict(
            range=[0.5, 5.5], 
            dtick=1,
            showgrid=True,
            gridcolor="lightgray",
            gridwidth=1,
            title=dict(
                text="<b>SPEND POTENTIAL</b><br>(how much budget available to spend with the agency?)",
                font=dict(size=12, color="darkgray"),
                standoff=40
            ),
            side="bottom",
            showline=True,
            linecolor="black",
            linewidth=3,
            mirror=False,
            tickfont=dict(size=11, color="black"),
            zeroline=False
        ),
        yaxis=dict(
            range=[0.5, 5.5], 
            dtick=1,
            showgrid=True,
            gridcolor="lightgray",
            gridwidth=1,
            title=dict(
                text="<b>STRATEGIC IMPORTANCE</b><br>(how important is this account to the agency?)",
                font=dict(size=12, color="darkgray"),
                standoff=60
            ),
            side="left",
            showline=True,
            linecolor="black",
            linewidth=3,
            mirror=False,
            tickfont=dict(size=11, color="black"),
            zeroline=False
        ),
        showlegend=True,
        legend=dict(
            title="Relationship Risk",
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            bgcolor="white",
            bordercolor="lightgray",
            borderwidth=1
        ),
        title=dict(
            text="<b>Client Categorisation Matrix</b>",
            font=dict(size=20, color="darkblue"),
            x=0.5,
            xanchor='center',
            y=0.95
        ),
        margin=dict(l=120, r=120, t=80, b=120)
    )
    
    # Add custom axis arrows using shapes and annotations
    # X-axis arrow (horizontal)
    fig.add_shape(
        type="line", x0=0.5, y0=0.5, x1=5.5, y1=0.5,
        line=dict(color="black", width=3)
    )
    fig.add_annotation(
        x=5.5, y=0.5, text="", showarrow=True,
        arrowhead=2, arrowsize=2, arrowwidth=3, arrowcolor="black",
        ax=5.3, ay=0.5
    )
    
    # Y-axis arrow (vertical)
    fig.add_shape(
        type="line", x0=0.5, y0=0.5, x1=0.5, y1=5.5,
        line=dict(color="black", width=3)
    )
    fig.add_annotation(
        x=0.5, y=5.5, text="", showarrow=True,
        arrowhead=2, arrowsize=2, arrowwidth=3, arrowcolor="black",
        ax=0.5, ay=5.3
    )
    
    # Add axis labels with positioning
    fig.add_annotation(
        x=5.7, y=0.3, text="HIGH", showarrow=False,
        font=dict(size=12, color="black", family="Arial Black")
    )
    fig.add_annotation(
        x=0.3, y=0.3, text="LOW", showarrow=False,
        font=dict(size=12, color="black", family="Arial Black")
    )
    fig.add_annotation(
        x=0.3, y=5.7, text="HIGH", showarrow=False,
        font=dict(size=12, color="black", family="Arial Black")
    )
    fig.add_annotation(
        x=0.3, y=0.8, text="LOW", showarrow=False,
        font=dict(size=12, color="black", family="Arial Black")
    )
    
    # Update hover template
    fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>" +
                      "Strategic Importance: %{y}<br>" +
                      "Spend Potential: %{x}<br>" +
                      "Relationship Risk: %{customdata[3]}<br>" +
                      "FY25 Revenue: £%{customdata[4]:,.0f}<br>" +
                      "% of Total Revenue: %{customdata[5]:.1f}%<br>" +
                      "<extra></extra>",
        customdata=df[['Client_Name', 'Strategic_Importance_(1-5)', 'Spend_Potential_(1-5)', 
                      'Relationship_Risk_(R/A/G)', 'FY25_Revenue', '%_of_Total_Revenue']].values
    )
    
    return fig

def main():
    """Main application function."""
    st.title("📊 Client Categorisation Matrix")
    st.markdown("---")
    
    # Data source selection
    st.subheader("Data Source")
    
    # Toggle between demo and user data
    data_mode = st.radio(
        "Choose data source:",
        ["Demo Data", "User Data"],
        horizontal=True,
        help="Demo Data: Use embedded sample data | User Data: Upload your own CSV or provide a URL"
    )
    
    df = None
    
    if data_mode == "Demo Data":
        st.info("Using embedded demo data for immediate testing and validation.")
        df = load_demo_data()
        df = clean_percentage_column(df)
        
        # Show data preview
        with st.expander("📋 View Demo Data", expanded=False):
            st.dataframe(df, use_container_width=True)
    
    else:  # User Data
        st.info("Upload your own CSV file or provide a URL to load custom data.")
        
        # Create two columns for input options
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Option 1: Upload CSV File**")
            uploaded_file = st.file_uploader(
                "Choose a CSV file",
                type=['csv'],
                help="Upload a CSV file with the required columns"
            )
            
            if uploaded_file is not None:
                df = load_data_from_file(uploaded_file)
        
        with col2:
            st.markdown("**Option 2: CSV URL**")
            csv_url = st.text_input(
                "Enter CSV URL:",
                placeholder="https://example.com/data.csv",
                help="Provide a direct link to a CSV file"
            )
            
            if csv_url and not uploaded_file:  # Only use URL if no file uploaded
                df = load_data_from_url(csv_url)
        
        # Show data preview if loaded
        if df is not None:
            with st.expander("📋 View Loaded Data", expanded=False):
                st.dataframe(df, use_container_width=True)
    
    # Validate and display chart
    if df is not None:
        if validate_data(df):
            st.markdown("---")
            st.subheader("📈 Visualization")
            
            # Create and display the plot
            fig = create_scatter_plot(df)
            st.plotly_chart(fig, use_container_width=True)
            
            # Download button
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("📥 Download Chart as PNG", type="primary", use_container_width=True):
                    # Convert plot to PNG
                    img_bytes = fig.to_image(format="png", width=1200, height=800, scale=2)
                    st.download_button(
                        label="💾 Save PNG File",
                        data=img_bytes,
                        file_name="client_categorisation_matrix.png",
                        mime="image/png",
                        use_container_width=True
                    )
            
            # Show data summary
            st.markdown("---")
            st.subheader("📊 Data Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Clients", len(df))
            
            with col2:
                total_revenue = df['FY25_Revenue'].sum()
                st.metric("Total Revenue", f"£{total_revenue:,.0f}")
            
            with col3:
                high_risk_count = len(df[df['Relationship_Risk_(R/A/G)'] == 'R'])
                st.metric("High Risk Clients", high_risk_count)
            
            with col4:
                avg_strategic_importance = df['Strategic_Importance_(1-5)'].mean()
                st.metric("Avg Strategic Importance", f"{avg_strategic_importance:.1f}")
            
            # Risk distribution
            st.markdown("**Risk Level Distribution:**")
            risk_counts = df['Relationship_Risk_(R/A/G)'].value_counts()
            risk_labels = {'R': 'Red (High Risk)', 'A': 'Amber (Medium Risk)', 'G': 'Green (Low Risk)'}
            
            for risk, count in risk_counts.items():
                percentage = (count / len(df)) * 100
                risk_str = str(risk)
                st.write(f"• {risk_labels.get(risk_str, risk_str)}: {count} clients ({percentage:.1f}%)")
        
        else:
            st.warning("Please ensure your data has all required columns.")
            st.markdown("""
            **Required columns:**
            - `Client_Name`
            - `Strategic_Importance_(1-5)`
            - `Spend_Potential_(1-5)`
            - `Relationship_Risk_(R/A/G)` (values: R, A, G)
            - `FY25_Revenue`
            - `%_of_Total_Revenue`
            """)
    
    else:
        if data_mode == "User Data":
            st.info("👆 Please upload a CSV file or provide a URL to load your data.")
            
            # Show data format requirements
            st.markdown("---")
            st.subheader("📋 Data Format Requirements")
            st.markdown("""
            Your CSV file must contain the following columns with exact names:
            
            | Column Name | Description | Expected Values |
            |-------------|-------------|-----------------|
            | `Client_Name` | Name of the client | Text |
            | `Strategic_Importance_(1-5)` | Strategic importance rating | Numbers 1-5 |
            | `Spend_Potential_(1-5)` | Potential spending rating | Numbers 1-5 |
            | `Relationship_Risk_(R/A/G)` | Risk level | R (Red), A (Amber), or G (Green) |
            | `FY25_Revenue` | Revenue for FY25 | Numeric values |
            | `%_of_Total_Revenue` | Percentage of total revenue | Numbers with or without % symbol |
            """)

if __name__ == "__main__":
    main()
