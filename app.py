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
import requests

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import PDFProcessor class
from PDFProcessor import PDFProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to load Lottie animations
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Custom CSS
def local_css():
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
            border-radius: 0.5rem;
        }
        .stButton>button {
            width: 100%;
            border-radius: 0.5rem;
            height: 3rem;
            font-weight: bold;
        }
        .upload-section {
            border: 2px dashed #cccccc;
            padding: 2rem;
            border-radius: 0.5rem;
            text-align: center;
            margin: 1rem 0;
        }
        .stats-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .success-message {
            padding: 1rem;
            background-color: #d4edda;
            color: #155724;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .error-message {
            padding: 1rem;
            background-color: #f8d7da;
            color: #721c24;
            border-radius: 0.5rem;
            margin: 1rem 0;
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
            <div class="stats-card">
                <h3>Files Processed</h3>
                <h2>{}</h2>
            </div>
            """.format(st.session_state.total_files_processed),
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            """
            <div class="stats-card">
                <h3>Successful</h3>
                <h2>{}</h2>
            </div>
            """.format(st.session_state.successful_conversions),
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            """
            <div class="stats-card">
                <h3>Failed</h3>
                <h2>{}</h2>
            </div>
            """.format(st.session_state.failed_conversions),
            unsafe_allow_html=True
        )

    if st.session_state.processing_history:
        # Create success rate chart
        fig = go.Figure()
        success_rate = (st.session_state.successful_conversions / 
                       st.session_state.total_files_processed * 100)
        
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=success_rate,
            title={'text': "Success Rate"},
            gauge={'axis': {'range': [None, 100]},
                  'steps': [
                      {'range': [0, 50], 'color': "lightgray"},
                      {'range': [50, 80], 'color': "gray"},
                      {'range': [80, 100], 'color': "darkgray"}],
                  'threshold': {
                      'line': {'color': "red", 'width': 4},
                      'thickness': 0.75,
                      'value': 90}}))
        
        st.plotly_chart(fig, use_container_width=True)

def display_processing_history():
    if st.session_state.processing_history:
        st.subheader("Processing History")
        history_df = pd.DataFrame(st.session_state.processing_history)
        st.dataframe(history_df, use_container_width=True)

def process_pdf(file_path):
    """Process the PDF file and return the path to the Excel output"""
    try:
        processor = PDFProcessor()
        processor.process_pdf(file_path)
        excel_path = file_path.replace('.pdf', '_Final.xlsx')
        return excel_path
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        logger.error(f"Processing error: {str(e)}")
        return None

def main():
    # Initialize session state
    initialize_session_state()
    
    # Apply custom CSS
    local_css()
    
    # Load animations
    lottie_upload = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_qmfs6c3i.json")
    lottie_processing = load_lottie_url("https://assets5.lottiefiles.com/private_files/lf30_4TwHil.json")
    
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
    st.markdown("### Upload Your PDF")
    uploaded_file = st.file_uploader(
        "Drag and drop your PDF file here",
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
            # Show processing animation
            with st.spinner(""):
                st_lottie(lottie_processing, height=200, key="processing")
                
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
                        
                        # Success message
                        st.success("✅ PDF processed successfully!")
                        
                        # Results section
                        st.markdown("### Results")
                        
                        # Preview tabs
                        tab1, tab2 = st.tabs(["📊 Preview", "📈 Statistics"])
                        
                        with tab1:
                            st.dataframe(df.head(10), use_container_width=True)
                            
                        with tab2:
                            # Display some statistics about the processed data
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
                    
                    st.error(f"An error occurred during processing: {str(e)}")
    
    # Display processing history
    if display_mode == "Detailed":
        display_processing_history()

if __name__ == "__main__":
    main()
