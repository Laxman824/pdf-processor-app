import streamlit as st
import tempfile
import os
import logging
from pathlib import Path
import pandas as pd
import fitz  # PyMuPDF
from PDFProcessor import PDFProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state for theme
if 'theme' not in st.session_state:
    st.session_state.theme = "light"

def get_theme_css():
    """Get theme-specific CSS"""
    if st.session_state.theme == "dark":
        return """
        <style>
            /* Dark theme styles */
            .stApp {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            .stButton button {
                background-color: #4A4A4A;
                color: #FFFFFF;
                border: 1px solid #666666;
            }
            .stButton button:hover {
                background-color: #666666;
            }
            div[data-testid="stFileUploader"] {
                background-color: #2D2D2D;
                border: 1px solid #666666;
            }
            div[data-testid="stMarkdown"] {
                color: #FFFFFF !important;
            }
            div[data-testid="stDataFrame"] {
                background-color: #2D2D2D;
            }
            .element-container {
                color: #FFFFFF;
            }
            .stAlert {
                background-color: #2D2D2D;
                color: #FFFFFF;
            }
            .css-1dp5vir {
                background-color: #2D2D2D;
                color: #FFFFFF;
            }
            .stMarkdown {
                color: #FFFFFF;
            }
            .stDataFrame {
                background-color: #2D2D2D;
            }
            .stDataFrame td {
                color: #FFFFFF;
            }
            .stDataFrame th {
                color: #FFFFFF;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #FFFFFF !important;
            }
            p {
                color: #FFFFFF !important;
            }
            .css-183lzff {
                color: #FFFFFF !important;
            }
            .css-10trblm {
                color: #FFFFFF !important;
            }
        </style>
        """
    else:
        return """
        <style>
            /* Light theme styles */
            .stApp {
                background-color: #FFFFFF;
                color: #000000;
            }
            .stButton button {
                background-color: #F0F2F6;
                color: #000000;
                border: 1px solid #CCCCCC;
            }
            .stButton button:hover {
                background-color: #E0E0E0;
            }
            div[data-testid="stMarkdown"] {
                color: #000000 !important;
            }
            .element-container {
                color: #000000;
            }
            .stMarkdown {
                color: #000000;
            }
            .css-1dp5vir {
                background-color: #F0F2F6;
                color: #000000;
            }
            .stDataFrame {
                background-color: #FFFFFF;
            }
            .stDataFrame td {
                color: #000000;
            }
            .stDataFrame th {
                color: #000000;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #000000 !important;
            }
            p {
                color: #000000 !important;
            }
            .css-183lzff {
                color: #000000 !important;
            }
            .css-10trblm {
                color: #000000 !important;
            }
        </style>
        """

def toggle_theme():
    """Toggle between light and dark theme"""
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

def save_uploaded_file(uploaded_file):
    """Save uploaded file to temporary directory and return the path"""
    try:
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / uploaded_file.name
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return str(temp_path)
    except Exception as e:
        st.error(f"Error saving uploaded file: {str(e)}")
        logger.error(f"File save error: {str(e)}")
        return None

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
    # Set page config
    st.set_page_config(
        page_title="PDF Footnote Processor",
        page_icon="📄",
        layout="wide"
    )

    # Inject custom CSS
    st.markdown(get_theme_css(), unsafe_allow_html=True)

    # Header with theme toggle
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("📄 PDF Footnote Processor")
    
    with col2:
        theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
        if st.button(f"{theme_icon} Toggle Theme"):
            toggle_theme()
            st.rerun()

    # Application description
    st.markdown("""
    This application processes PDF documents and extracts content with footnotes into an organized Excel file.
    
    ### Features:
    - Detects and extracts footnotes automatically
    - Maintains text formatting and structure
    - Generates formatted Excel output
    """)

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload your PDF file",
        type=['pdf'],
        help="Upload a PDF file to process"
    )

    if uploaded_file:
        # Display file info
        text_color = "#FFFFFF" if st.session_state.theme == "dark" else "#000000"
        bg_color = "#2D2D2D" if st.session_state.theme == "dark" else "#F0F2F6"
        
        st.markdown(f"""
        <div style='padding: 1rem; border-radius: 0.5rem; background-color: {bg_color}; margin: 1rem 0;'>
            <h3 style='margin-bottom: 0.5rem; color: {text_color};'>File Details:</h3>
        """, unsafe_allow_html=True)
        
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB",
            "File type": uploaded_file.type
        }
        
        for key, value in file_details.items():
            st.markdown(f"<p style='color: {text_color};'>- {key}: {value}</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Process button
        if st.button("Process PDF", type="primary"):
            with st.spinner("Processing PDF... This may take a few moments."):
                try:
                    # Save and process file
                    temp_path = save_uploaded_file(uploaded_file)
                    if temp_path:
                        excel_path = process_pdf(temp_path)
                        
                        if excel_path and os.path.exists(excel_path):
                            # Read and display preview
                            df = pd.read_excel(excel_path)
                            st.success("✅ PDF processed successfully!")
                            
                            st.subheader("Preview of Processed Content")
                            st.dataframe(
                                df.head(10),
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            # Download button
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
                    st.error(f"An error occurred during processing: {str(e)}")
                    logger.error(f"Processing error: {str(e)}")

    # Footer
    st.markdown("---")
    text_color = "#FFFFFF" if st.session_state.theme == "dark" else "#000000"
    st.markdown(f"""
    <div style='color: {text_color};'>
    
    ### Instructions:
    1. Upload your PDF file using the file uploader above
    2. Click the "Process PDF" button to start processing
    3. Preview the results and download the Excel file
    
    > Note: Large PDF files may take longer to process. Please be patient.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
