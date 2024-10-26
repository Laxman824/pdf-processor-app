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

# Custom CSS for light/dark mode
def get_theme_css():
    if st.session_state.theme == "dark":
        return """
        <style>
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
                color: #FFFFFF;
            }
            div[data-testid="stDataFrame"] {
                background-color: #2D2D2D;
            }
            div.element-container {
                background-color: #1E1E1E;
            }
            .stAlert {
                background-color: #2D2D2D;
                color: #FFFFFF;
            }
        </style>
        """
    else:
        return """
        <style>
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
        </style>
        """

# Toggle theme function
def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# Set page config
st.set_page_config(
    page_title="PDF Footnote Processor",
    page_icon="📄",
    layout="wide"
)

# Inject custom CSS
st.markdown(get_theme_css(), unsafe_allow_html=True)

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
        return None

def main():
    # Header container with theme toggle
    header_col1, header_col2 = st.columns([4, 1])
    
    with header_col1:
        st.title("📄 PDF Footnote Processor")
    
    with header_col2:
        # Theme toggle button
        theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
        if st.button(f"{theme_icon} Toggle Theme"):
            toggle_theme()
            st.rerun()
    
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
        # Display file info in a card-like container
        with st.container():
            st.markdown("""
            <div style='padding: 1rem; border-radius: 0.5rem; background-color: {}; margin: 1rem 0;'>
                <h3 style='margin-bottom: 0.5rem; color: {};'>File Details:</h3>
            """.format(
                "#2D2D2D" if st.session_state.theme == "dark" else "#F0F2F6",
                "#FFFFFF" if st.session_state.theme == "dark" else "#000000"
            ), unsafe_allow_html=True)
            
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.2f} KB",
                "File type": uploaded_file.type
            }
            for key, value in file_details.items():
                st.write(f"- {key}: {value}")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Process button
        if st.button("Process PDF", type="primary"):
            with st.spinner("Processing PDF... This may take a few moments."):
                try:
                    temp_path = save_uploaded_file(uploaded_file)
                    if temp_path:
                        excel_path = process_pdf(temp_path)
                        
                        if excel_path and os.path.exists(excel_path):
                            df = pd.read_excel(excel_path)
                            
                            st.success("✅ PDF processed successfully!")
                            
                            st.subheader("Preview of Processed Content")
                            st.dataframe(
                                df.head(10),
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            with open(excel_path, "rb") as file:
                                excel_data = file.read()
                                st.download_button(
                                    label="📥 Download Excel File",
                                    data=excel_data,
                                    file_name=f"{uploaded_file.name.replace('.pdf', '_Final.xlsx')}",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                            
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
    st.markdown(f"""
    <div style='color: {"#FFFFFF" if st.session_state.theme == "dark" else "#000000"}'>
    
    ### Instructions:
    1. Upload your PDF file using the file uploader above
    2. Click the "Process PDF" button to start processing
    3. Preview the results and download the Excel file
    
    > Note: Large PDF files may take longer to process. Please be patient.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
