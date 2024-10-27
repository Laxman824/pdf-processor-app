import streamlit as st
import tempfile
import time
import base64
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
def auto_download(excel_data, filename):
    """Create auto-download functionality using JavaScript"""
    b64 = base64.b64encode(excel_data).decode()
    
    # Create the JavaScript auto-download
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

# Replace the existing download section in your main() function with this:
if excel_path and os.path.exists(excel_path):
    df = pd.read_excel(excel_path)
    
    # Success message with animation
    st.markdown("""
        <div class="animate-slide-in" style="margin: 1rem 0;">
            <div style="padding: 1rem; background-color: #d1e7dd; color: #0f5132; border-radius: 0.5rem;">
                ✅ PDF processed successfully!
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Preview Card
    st.markdown("""
        <div class="animate-fade-in">
            <h3 style="font-size: 1.3rem; font-weight: 600; margin: 1rem 0;">
                Preview of Processed Content
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.dataframe(
        df.head(10),
        use_container_width=True,
        hide_index=True
    )
    
    # Read excel file and prepare for download
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
        st.markdown("""
            <div style="margin-top: 1rem; padding: 0.8rem; background-color: #e7f3fe; color: #0c5460; border-radius: 0.5rem;">
                💡 Your file will automatically download in 3 seconds if not downloaded manually.
            </div>
        """, unsafe_allow_html=True)
        
    # Add countdown timer (optional)
    countdown_placeholder = st.empty()
    for i in range(3, 0, -1):
        countdown_placeholder.markdown(f"""
            <div style="text-align: center; color: #666;">
                Auto-download in {i} seconds...
            </div>
        """, unsafe_allow_html=True)
        time.sleep(1)
    countdown_placeholder.empty()
def create_custom_card(title, content, theme):
    """Create a custom styled card"""
    bg_color = "#2D2D2D" if theme == "dark" else "#F8F9FA"
    text_color = "#FFFFFF" if theme == "dark" else "#000000"
    border_color = "#404040" if theme == "dark" else "#E9ECEF"
    
    return f"""
    <div class="custom-card animate-fade-in" 
         style="background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color};">
        <h3 style="color: {text_color}; margin-bottom: 1rem;">{title}</h3>
        {content}
    </div>
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
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Inject custom CSS
    st.markdown(get_theme_css(), unsafe_allow_html=True)

    # Header with animated title
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("""
            <div class="animate-slide-in">
                <h1 style="font-size: 2.5rem; font-weight: 700;">📄 PDF Footnote Processor</h1>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
        if st.button(f"{theme_icon} Theme", key="theme_toggle"):
            toggle_theme()
            st.rerun()

    # Introduction Card
    intro_content = """
    <p style="font-size: 1.1rem; line-height: 1.6;">
        Transform your PDF documents with our advanced footnote processing tool.
        Upload your PDF and get an organized Excel file with extracted content and footnotes.
    </p>
    <div style="margin-top: 1rem;">
        <h4 style="font-weight: 600;">Key Features:</h4>
        <ul style="list-style-type: none; padding-left: 0;">
            <li style="margin: 0.5rem 0;">✨ Automatic footnote detection and extraction</li>
            <li style="margin: 0.5rem 0;">📝 Maintains text formatting and structure</li>
            <li style="margin: 0.5rem 0;">📊 Generates formatted Excel output</li>
        </ul>
    </div>
    """
    st.markdown(create_custom_card("Welcome", intro_content, st.session_state.theme), unsafe_allow_html=True)

    # File Upload Section
    st.markdown("""
        <div class="animate-fade-in" style="margin-top: 2rem;">
            <h2 style="font-size: 1.5rem; font-weight: 600;">Upload Your PDF</h2>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF file to process"
    )

    if uploaded_file:
        # File Details Card
        file_details = {
            "📄 Filename": uploaded_file.name,
            "📦 Size": f"{uploaded_file.size / 1024:.2f} KB",
            "📋 Type": uploaded_file.type
        }
        
        details_content = "".join([
            f"<div style='display: flex; align-items: center; margin: 0.5rem 0;'>"
            f"<span style='font-weight: 500; margin-right: 1rem;'>{key}:</span>"
            f"<span>{value}</span></div>"
            for key, value in file_details.items()
        ])
        
        st.markdown(create_custom_card("File Details", details_content, st.session_state.theme), unsafe_allow_html=True)

        # Process Button with enhanced styling
        if st.button("🚀 Process PDF", type="primary"):
            with st.spinner("📊 Processing your PDF..."):
                try:
                    temp_path = save_uploaded_file(uploaded_file)
                    if temp_path:
                        excel_path = process_pdf(temp_path)
                        
                        if excel_path and os.path.exists(excel_path):
                            df = pd.read_excel(excel_path)
                            
                            # Success message with animation
                            st.markdown("""
                                <div class="animate-slide-in" style="margin: 1rem 0;">
                                    <div style="padding: 1rem; background-color: #d1e7dd; color: #0f5132; border-radius: 0.5rem;">
                                        ✅ PDF processed successfully!
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Preview Card
                            st.markdown("""
                                <div class="animate-fade-in">
                                    <h3 style="font-size: 1.3rem; font-weight: 600; margin: 1rem 0;">
                                        Preview of Processed Content
                                    </h3>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            st.dataframe(
                                df.head(10),
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            # Download button with custom styling
                            with open(excel_path, "rb") as file:
                                excel_data = file.read()
                                st.download_button(
                                    label="📥 Download Excel File",
                                    data=excel_data,
                                    file_name=f"{uploaded_file.name.replace('.pdf', '_processed.xlsx')}",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                            
                            # Cleanup
                            try:
                                os.remove(temp_path)
                                os.remove(excel_path)
                            except Exception as e:
                                logger.error(f"Error cleaning up temporary files: {str(e)}")
                
                except Exception as e:
                    st.error(f"❌ An error occurred during processing: {str(e)}")
                    logger.error(f"Processing error: {str(e)}")

    # Instructions Card
    instructions_content = """
    <ol style="list-style-type: none; padding-left: 0;">
        <li style="margin: 0.8rem 0;">1️⃣ Upload your PDF file using the uploader above</li>
        <li style="margin: 0.8rem 0;">2️⃣ Click the "Process PDF" button to start processing</li>
        <li style="margin: 0.8rem 0;">3️⃣ Preview the results and download your Excel file</li>
    </ol>
    <div style="margin-top: 1rem; padding: 0.8rem; background-color: rgba(255, 255, 255, 0.1); border-radius: 0.5rem;">
        <p style="margin: 0;">
            <strong>Note:</strong> Large PDF files may take longer to process. Please be patient.
        </p>
    </div>
    """
    st.markdown(create_custom_card("Instructions", instructions_content, st.session_state.theme), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
