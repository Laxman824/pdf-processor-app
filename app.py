import streamlit as st
import tempfile
import os
import logging
import time
import base64
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
def get_base64_of_file(file_path):
    """Get base64 encoded version of a local file"""
    return base64.b64encode(Path(file_path).read_bytes()).decode()

def set_page_icon(gif_path):
    """Set page icon using local GIF"""
    base64_gif = get_base64_of_file(gif_path)
    return f"data:image/gif;base64,{base64_gif}"

# In your main function
def main():
    # Set the icon using local GIF
    icon_path = "assets/pdf.gif"  # Path to your GIF
    page_icon = set_page_icon(icon_path)

    st.set_page_config(
        page_title="PDF Footnote Processor",
        page_icon=page_icon,
        layout="wide"
    )
class IconManager:
    def __init__(self, gif_path):
        self.gif_path = gif_path
        self._validate_path()

    def _validate_path(self):
        """Validate that the GIF file exists"""
        if not os.path.exists(self.gif_path):
            raise FileNotFoundError(f"GIF file not found at: {self.gif_path}")

    def get_base64(self):
        """Get base64 encoded version of the GIF"""
        return base64.b64encode(Path(self.gif_path).read_bytes()).decode()

    def get_page_icon(self):
        """Get data URL for page icon"""
        return f"data:image/gif;base64,{self.get_base64()}"

    def get_html_img(self, size=30):
        """Get HTML img tag with the GIF"""
        return f"""
            <img src="data:image/gif;base64,{self.get_base64()}" 
                 width="{size}px" 
                 height="{size}px"
                 style="object-fit: contain;"/>
        """

def main():
    # Initialize icon manager
    try:
        icon_manager = IconManager("assets/pdf_icon.gif")
        
        # Set page config with GIF icon
        st.set_page_config(
            page_title="PDF Footnote Processor",
            page_icon=icon_manager.get_page_icon(),
            layout="wide"
        )

        # Header with GIF and title
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; gap: 10px;">
                    {icon_manager.get_html_img(size=40)}
                    <h1 class="animate-slide-in" style="margin: 0;">
                        PDF Footnote Processor
                    </h1>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
            if st.button(f"{theme_icon} Theme", key="theme_toggle"):
                toggle_theme()
                st.rerun()

    except FileNotFoundError:
        # Fallback to emoji if GIF not found
        st.set_page_config(
            page_title="PDF Footnote Processor",
            page_icon="📑",
            layout="wide"
        )
        st.error("Custom icon not found. Using default icon.")

def get_theme_css():
    """Enhanced CSS with animations and hover effects"""
    base_styles = """
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideIn {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        /* Common Styles */
        .animate-fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        .animate-slide-in {
            animation: slideIn 0.5s ease-out;
        }
        
        /* Card Styles */
        .custom-card {
            border-radius: 1rem;
            padding: 1.5rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .custom-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
        }
        
        /* Button Styles */
        .stButton button {
            transition: all 0.3s ease !important;
            border-radius: 0.5rem !important;
            font-weight: 500 !important;
            padding: 0.5rem 1rem !important;
        }
        
        /* File Uploader Styles */
        [data-testid="stFileUploader"] {
            border-radius: 1rem !important;
            transition: all 0.3s ease;
        }
        
        [data-testid="stFileUploader"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Alert Styles */
        .stAlert {
            border-radius: 0.5rem !important;
            animation: slideIn 0.5s ease-out;
        }
        /* Add this to your CSS in get_theme_css() */
        .stDownloadButton button {
            background: linear-gradient(145deg, #2ea043, #238636) !important;
            color: #FFFFFF !important;
            border: none !important;
            padding: 0.75rem 1.5rem !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 0.5rem !important;
            transition: all 0.3s ease !important;
        }

        .stDownloadButton button:hover {
            background: linear-gradient(145deg, #3fb950, #2ea043) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(46, 160, 67, 0.4) !important;
        }

        /* Download notification style */
        .download-notification {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 1rem;
            background-color: #f8f9fa;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            animation: slideIn 0.3s ease-out;
            z-index: 1000;
        }

        @keyframes slideIn {
            from {
                transform: translateY(100%);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        /* DataFrame Styles */
        [data-testid="stTable"] {
            border-radius: 0.5rem !important;
            overflow: hidden;
        }
        
        /* Progress Bar Animation */
        .stProgress > div > div {
            transition: width 0.3s ease-in-out;
        }
    """

    if st.session_state.theme == "dark":
        return f"""
        <style>
            {base_styles}
            
            /* Dark Theme Specific */
            .stApp {{
                background-color: #1E1E1E;
                color: #FFFFFF;
                transition: all 0.3s ease;
            }}
            
            .custom-card {{
                background-color: #2D2D2D;
                border: 1px solid #404040;
            }}
            
            .stButton button {{
                background: linear-gradient(145deg, #4A4A4A, #333333) !important;
                color: #FFFFFF !important;
                border: none !important;
            }}
            
            .stButton button:hover {{
                background: linear-gradient(145deg, #555555, #444444) !important;
                transform: translateY(-2px);
            }}
            
            .stDownloadButton button {{
                background: linear-gradient(145deg, #2ea043, #238636) !important;
                color: #FFFFFF !important;
            }}
            
            .stDownloadButton button:hover {{
                background: linear-gradient(145deg, #3fb950, #2ea043) !important;
            }}
            
            [data-testid="stFileUploader"] {{
                background-color: #2D2D2D !important;
                border: 2px dashed #404040 !important;
            }}
            
            [data-testid="stFileUploader"]:hover {{
                border-color: #666666 !important;
            }}
            
            .stDataFrame {{
                background-color: #2D2D2D;
            }}
            
            .stDataFrame td {{
                color: #FFFFFF !important;
            }}
            
            .stDataFrame th {{
                background-color: #404040 !important;
                color: #FFFFFF !important;
            }}
            
            h1, h2, h3, h4, h5, h6 {{
                color: #FFFFFF !important;
            }}
            
            p {{
                color: #FFFFFF !important;
            }}
        </style>
        """
    else:
        return f"""
        <style>
            {base_styles}
            
            /* Light Theme Specific */
            .stApp {{
                background-color: #FFFFFF;
                color: #000000;
                transition: all 0.3s ease;
            }}
            
            .custom-card {{
                background-color: #F8F9FA;
                border: 1px solid #E9ECEF;
            }}
            
            .stButton button {{
                background: linear-gradient(145deg, #F8F9FA, #E9ECEF) !important;
                color: #000000 !important;
                border: 1px solid #DEE2E6 !important;
            }}
            
            .stButton button:hover {{
                background: linear-gradient(145deg, #E9ECEF, #DEE2E6) !important;
                transform: translateY(-2px);
            }}
            
            .stDownloadButton button {{
                background: linear-gradient(145deg, #2ea043, #238636) !important;
                color: #FFFFFF !important;
            }}
            
            .stDownloadButton button:hover {{
                background: linear-gradient(145deg, #3fb950, #2ea043) !important;
            }}
            
            [data-testid="stFileUploader"] {{
                background-color: #F8F9FA !important;
                border: 2px dashed #DEE2E6 !important;
            }}
            
            [data-testid="stFileUploader"]:hover {{
                border-color: #ADB5BD !important;
            }}
            
            .stDataFrame {{
                background-color: #FFFFFF;
            }}
            
            .stDataFrame td {{
                color: #000000 !important;
            }}
            
            .stDataFrame th {{
                background-color: #F8F9FA !important;
                color: #000000 !important;
            }}
            
            h1, h2, h3, h4, h5, h6 {{
                color: #000000 !important;
            }}
            
            p {{
                color: #000000 !important;
            }}
        </style>
        """
def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

def auto_download(excel_data, filename):
    """Create auto-download functionality using JavaScript"""
    b64 = base64.b64encode(excel_data).decode()
    
    auto_download_js = f"""
        <script>
            function downloadFile() {{
                const link = document.createElement('a');
                link.href = "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}";
                link.download = "{filename}";
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }}
            
            // Set timeout for auto-download
            setTimeout(function() {{
                if (!window.downloaded) {{
                    downloadFile();
                    window.downloaded = true;
                }}
            }}, 3000);
        </script>
    """
    
    return auto_download_js

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
    # Set page config with custom icon
    st.set_page_config(
        page_title="PDF Footnote Processor",
        page_icon="",  # Using a different PDF-related emoji
        layout="wide"
    )

    # Inject custom CSS
    st.markdown(get_theme_css(), unsafe_allow_html=True)

    # Header with theme toggle
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("📑 PDF Footnote Processor")
    
    with col2:
        theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
        if st.button(f"{theme_icon} Theme", key="theme_toggle"):
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
                    # Save and process file
                    temp_path = save_uploaded_file(uploaded_file)
                    if temp_path:
                        excel_path = process_pdf(temp_path)
                        
                        if excel_path and os.path.exists(excel_path):
                            # Read the Excel file
                            df = pd.read_excel(excel_path)
                            
                            # Success message
                            st.success("✅ PDF processed successfully!")
                            
                            # Preview section
                            st.subheader("Preview of Processed Content")
                            st.dataframe(
                                df.head(10),
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            # Read excel file for download
                            with open(excel_path, "rb") as file:
                                excel_data = file.read()
                                output_filename = f"{uploaded_file.name.replace('.pdf', '_processed.xlsx')}"
                                
                                # Manual download button
                                st.download_button(
                                    label="📥 Download Excel File",
                                    data=excel_data,
                                    file_name=output_filename,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key='manual_download'
                                )
                                
                                # Add auto-download functionality
                                st.markdown(auto_download(excel_data, output_filename), unsafe_allow_html=True)
                                
                                # Add download status message
                                st.info("💡 Your file will automatically download in 3 seconds if not downloaded manually.")
                            
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