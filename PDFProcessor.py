import streamlit as st
import tempfile
import os
import logging
from pathlib import Path
import pandas as pd
import fitz
import time
import sys
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import json

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import PDFProcessor class
from PDFProcessor import PDFProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lottie animations as JSON
LOTTIE_ANIMATION = {
    "v": "5.7.4",
    "fr": 30,
    "ip": 0,
    "op": 60,
    "w": 512,
    "h": 512,
    "nm": "Loading Animation",
    "ddd": 0,
    "assets": [],
    "layers": [{
        "ddd": 0,
        "ind": 1,
        "ty": 4,
        "nm": "Circle",
        "sr": 1,
        "ks": {
            "o": {"a": 0, "k": 100},
            "r": {
                "a": 1,
                "k": [{
                    "i": {"x": [0.833], "y": [0.833]},
                    "o": {"x": [0.167], "y": [0.167]},
                    "t": 0,
                    "s": [0]
                }, {
                    "t": 60,
                    "s": [360]
                }]
            },
            "p": {"a": 0, "k": [256, 256]},
            "a": {"a": 0, "k": [0, 0, 0]},
            "s": {"a": 0, "k": [100, 100, 100]}
        },
        "shapes": [{
            "ty": "el",
            "p": {"a": 0, "k": [0, 0]},
            "s": {"a": 0, "k": [200, 200]},
            "d": 1,
            "nm": "Circle Path"
        }, {
            "ty": "st",
            "c": {"a": 0, "k": [0.2, 0.5, 1]},
            "o": {"a": 0, "k": 100},
            "w": {"a": 0, "k": 20},
            "lc": 2,
            "lj": 1,
            "ml": 4,
            "nm": "Stroke"
        }, {
            "ty": "tm",
            "s": {"a": 0, "k": 0},
            "e": {"a": 0, "k": 25},
            "o": {"a": 0, "k": 0},
            "nm": "Trim Paths"
        }]
    }]
}

# Custom CSS with improved styling
def local_css():
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .main {
            padding: 2rem;
            border-radius: 0.5rem;
        }
        .stButton>button {
            width: 100%;
            border-radius: 0.5rem;
            height: 3rem;
            font-weight: bold;
            background-color: #4CAF50;
            color: white;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #45a049;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .upload-section {
            border: 2px dashed #4CAF50;
            padding: 2rem;
            border-radius: 0.5rem;
            text-align: center;
            margin: 1rem 0;
            background-color: #f8f9fa;
        }
        .stats-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .stats-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .success-message {
            padding: 1rem;
            background-color: #d4edda;
            color: #155724;
            border-radius: 0.5rem;
            margin: 1rem 0;
            animation: fadeIn 0.5s ease-in;
        }
        .error-message {
            padding: 1rem;
            background-color: #f8d7da;
            color: #721c24;
            border-radius: 0.5rem;
            margin: 1rem 0;
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #4CAF50;
        }
        .metric-label {
            color: #666;
            font-size: 0.9rem;
        }
        </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    if 'processing_history' not in st.session_state:
        st.session_state.processing_history = []
    if 'total_files_processed' not in st.session_state:
        st.session_state.total_files_processed = 0
    if 'successful_conversions' not in st.session_state:
        st.session_state.successful_conversions = 0
    if 'failed_conversions' not in st.session_state:
        st.session_state.failed_conversions = 0

def display_statistics():
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-value">{}</div>
                <div class="metric-label">Files Processed</div>
            </div>
            """.format(st.session_state.total_files_processed),
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-value">{}</div>
                <div class="metric-label">Successful</div>
            </div>
            """.format(st.session_state.successful_conversions),
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-value">{}</div>
                <div class="metric-label">Failed</div>
            </div>
            """.format(st.session_state.failed_conversions),
            unsafe_allow_html=True
        )

    if st.session_state.total_files_processed > 0:
        success_rate = (st.session_state.successful_conversions / 
                       st.session_state.total_files_processed * 100)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=success_rate,
            title={'text': "Success Rate"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#4CAF50"},
                'steps': [
                    {'range': [0, 50], 'color': "#ffebee"},
                    {'range': [50, 80], 'color': "#e8f5e9"},
                    {'range': [80, 100], 'color': "#c8e6c9"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def display_processing_history():
    if st.session_state.processing_history:
        st.subheader("Processing History")
        
        # Convert history to DataFrame
        history_df = pd.DataFrame(st.session_state.processing_history)
        
        # Style the dataframe
        def color_status(val):
            color = '#d4edda' if val == 'Success' else '#f8d7da'
            return f'background-color: {color}'
        
        styled_df = history_df.style.applymap(color_status, subset=['Status'])
        st.dataframe(styled_df, use_container_width=True)

def main():
    # Initialize session state
    initialize_session_state()
    
    # Apply custom CSS
    local_css()
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Settings")
        st.markdown("---")
        
        # Theme selection
        theme = st.selectbox(
            "Choose Theme",
            ["Light", "Dark"],
            key="theme"
        )
        
        # Display mode
        display_mode = st.radio(
            "Display Mode",
            ["Compact", "Detailed"]
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This app processes PDF documents and extracts content with footnotes 
        into organized Excel files. Perfect for document analysis and content extraction.
        """)
    
    # Main content
    st.title("📄 PDF Footnote Processor")
    st.markdown("---")
    
    # Display statistics
    display_statistics()
    
    # File upload section
    st.markdown(
        """
        <div class="upload-section">
            <h3>Upload Your PDF</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    uploaded_file = st.file_uploader(
        "",  # Empty label since we're using custom HTML
        type=['pdf'],
        help="Upload a PDF file to process"
    )
    
    if uploaded_file:
        # File details section
        with st.expander("📑 File Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Filename:** {uploaded_file.name}")
                st.markdown(f"**Size:** {uploaded_file.size / 1024:.2f} KB")
            with col2:
                st.markdown(f"**Type:** {uploaded_file.type}")
                st.markdown(f"**Uploaded at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Process button
        if st.button("🚀 Process PDF", type="primary"):
            with st.spinner("Processing your PDF..."):
                # Show processing animation
                st_lottie(LOTTIE_ANIMATION, height=200, key="processing")
                
                try:
                    # Save uploaded file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        temp_path = tmp_file.name
                    
                    # Process the PDF
                    excel_path = process_pdf(temp_path)
                    
                    if excel_path and os.path.exists(excel_path):
                        # Update statistics
                        st.session_state.total_files_processed += 1
                        st.session_state.successful_conversions += 1
                        
                        # Add to history
                        st.session_state.processing_history.append({
                            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'Filename': uploaded_file.name,
                            'Status': 'Success',
                            'Size': f"{uploaded_file.size / 1024:.2f} KB"
                        })
                        
                        # Read the Excel file
                        df = pd.read_excel(excel_path)
                        
                        # Success message with animation
                        st.markdown(
                            """
                            <div class="success-message">
                                ✅ PDF processed successfully!
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        # Results section
                        st.markdown("### Results")
                        
                        # Preview tabs
                        tab1, tab2 = st.tabs(["📊 Preview", "📈 Statistics"])
                        
                        with tab1:
                            st.dataframe(df.head(10), use_container_width=True)
                            
                        with tab2:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Total Rows", len(df))
                            with col2:
                                st.metric("Footnotes Found", len(df[df['Footnotes'].notna()]))
                        
                        # Download section
                        st.markdown("### Download")
                        with open(excel_path, "rb") as file:
                            excel_data = file.read()
                            st.download_button(
                                label="📥 Download Excel File",
                                data=excel_data,
                                file_name=f"{uploaded_file.name.replace('.pdf', '_Final.xlsx')}",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        
                        # Cleanup
                        try:
                            os.remove(temp_path)
                            os.remove(excel_path)
                        except Exception as e:
                            logger.error(f"Error cleaning up temporary files: {str(e)}")
                    
                except Exception as e:
                    # Update statistics
                    st.session_state.total_files_processed += 1
                    st.session_state.failed_conversions += 1
                    
                    # Add to history
                    st.session_state.processing_history.append({
                        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Filename': uploaded_file.name,
                        'Status': 'Failed',
                        'Size': f"{uploaded_file.size / 1024:.2f} KB"
                    })
                    
                    st.markdown(
                        f"""
                        <div class="error-message">
                            ❌ An error occurred during processing: {str(e)}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
    
    # Display processing history
    if display_mode == "Detailed":
        display_processing_history()

if __name__ == "__main__":
    main()
