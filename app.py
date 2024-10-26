import streamlit as st
import tempfile
import os
import logging
from pathlib import Path
import pandas as pd
import fitz  # PyMuPDF
from PDFProcessor import PDFProcessor  # Assuming the original code is in PDFProcessor.py

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="PDF Footnote Processor",
    page_icon="📄",
    layout="wide"
)

def save_uploaded_file(uploaded_file):
    """Save uploaded file to temporary directory and return the path"""
    try:
        # Create a temporary directory if it doesn't exist
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        # Create temporary file path
        temp_path = temp_dir / uploaded_file.name
        
        # Write uploaded file to temporary location
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
    # Header
    st.title("📄 PDF Footnote Processor")
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
        st.write("File Details:")
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB",
            "File type": uploaded_file.type
        }
        for key, value in file_details.items():
            st.write(f"- {key}: {value}")
        
        # Process button
        if st.button("Process PDF", type="primary"):
            with st.spinner("Processing PDF... This may take a few moments."):
                try:
                    # Save uploaded file
                    temp_path = save_uploaded_file(uploaded_file)
                    if temp_path:
                        # Process the PDF
                        excel_path = process_pdf(temp_path)
                        
                        if excel_path and os.path.exists(excel_path):
                            # Read the Excel file to display preview
                            df = pd.read_excel(excel_path)
                            
                            # Success message
                            st.success("✅ PDF processed successfully!")
                            
                            # Preview section
                            st.subheader("Preview of Processed Content")
                            st.dataframe(df.head(10), use_container_width=True)
                            
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
    st.markdown("""
    ### Instructions:
    1. Upload your PDF file using the file uploader above
    2. Click the "Process PDF" button to start processing
    3. Preview the results and download the Excel file
    
    > Note: Large PDF files may take longer to process. Please be patient.
    """)

if __name__ == "__main__":
    main()
