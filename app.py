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

def get_base64_of_file(file_path):
    """Get base64 encoded version of a local file"""
    return base64.b64encode(Path(file_path).read_bytes()).decode()

def get_theme_css():
    """Get theme-specific CSS with enhanced styling"""
    base_styles = """
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes slideIn {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }

    .main-title {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        background: linear-gradient(120deg, #1a5f7a, #57c7ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: fadeIn 1s ease-out;
    }

    .pdf-gif {
        animation: float 3s ease-in-out infinite;
    }

    .feature-card {
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        animation: slideIn 0.5s ease-out;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
    }

    .upload-section {
        padding: 2rem;
        border-radius: 1rem;
        margin: 2rem 0;
        transition: all 0.3s ease;
    }

    .stButton button {
        transition: all 0.3s ease !important;
        transform: scale(1);
    }

    .stButton button:hover {
        transform: scale(1.05);
    }

    .download-button {
        background: linear-gradient(45deg, #2ea043, #238636) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 0.5rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }

    .download-button:hover {
        background: linear-gradient(45deg, #3fb950, #2ea043) !important;
        box-shadow: 0 4px 12px rgba(46, 160, 67, 0.4) !important;
    }
    """

    if st.session_state.theme == "dark":
        return f"""
        <style>
            {base_styles}
            .stApp {{
                background-color: #1E1E1E;
                color: #FFFFFF;
            }}
            .feature-card {{
                background-color: #2D2D2D;
                border: 1px solid #404040;
            }}
            .upload-section {{
                background-color: #2D2D2D;
                border: 2px dashed #404040;
            }}
            [data-testid="stFileUploader"] {{
                background-color: #2D2D2D !important;
            }}
        </style>
        """
    else:
        return f"""
        <style>
            {base_styles}
            .stApp {{
                background-color: #FFFFFF;
                color: #000000;
            }}
            .feature-card {{
                background-color: #F8F9FA;
                border: 1px solid #E9ECEF;
            }}
            .upload-section {{
                background-color: #F8F9FA;
                border: 2px dashed #DEE2E6;
            }}
            [data-testid="stFileUploader"] {{
                background-color: #F8F9FA !important;
            }}
        </style>
        """

def create_title_with_gif():
    """Create animated title with PDF GIF"""
    gif_path = "assets/pdf.gif"
    if os.path.exists(gif_path):
        gif_base64 = get_base64_of_file(gif_path)
        return f"""
        <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 2rem;">
            <h1 class="main-title">PDF Footnote Processor</h1>
            <img src="data:image/gif;base64,{gif_base64}" 
                 class="pdf-gif"
                 style="width: 60px; height: 60px; object-fit: contain;">
        </div>
        """
    return '<h1 class="main-title">PDF Footnote Processor</h1>'

def create_auto_download_button(excel_data, filename):
    """Create auto-download button with enhanced UI"""
    b64 = base64.b64encode(excel_data).decode()
    
    return f"""
        <script>
            async function downloadFile() {{
                await new Promise(resolve => setTimeout(resolve, 3000));
                if (!window.manualDownload) {{
                    const link = document.createElement('a');
                    link.href = "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}";
                    link.download = "{filename}";
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    // Show notification
                    const notification = document.createElement('div');
                    notification.innerHTML = `
                        <div style="
                            position: fixed;
                            bottom: 20px;
                            right: 20px;
                            background: linear-gradient(45deg, #2ea043, #238636);
                            color: white;
                            padding: 1rem;
                            border-radius: 0.5rem;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                            animation: slideIn 0.5s ease-out;
                            z-index: 9999;
                        ">
                            ✅ File downloaded successfully!
                        </div>
                    `;
                    document.body.appendChild(notification);
                    setTimeout(() => notification.remove(), 3000);
                }}
            }}
            downloadFile();
        </script>
    """

def main():
    st.set_page_config(
        page_title="PDF Footnote Processor",
        page_icon="📑",
        layout="wide"
    )

    st.markdown(get_theme_css(), unsafe_allow_html=True)
    
    # Title with GIF
    st.markdown(create_title_with_gif(), unsafe_allow_html=True)
    
    # Theme toggle
    col1, col2 = st.columns([6, 1])
    with col2:
        theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
        if st.button(f"{theme_icon} Theme", key="theme_toggle"):
            st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
            st.rerun()

    # Feature cards
    st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin: 2rem 0;">
            <div class="feature-card">
                <h3 style="font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem;">📝 Automatic Detection</h3>
                <p>Smart footnote detection and extraction from your PDF documents.</p>
            </div>
            <div class="feature-card">
                <h3 style="font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem;">🎯 Precise Formatting</h3>
                <p>Maintains original text structure and formatting integrity.</p>
            </div>
            <div class="feature-card">
                <h3 style="font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem;">📊 Excel Export</h3>
                <p>Organized output in Excel format for easy analysis.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload your PDF file",
        type=['pdf'],
        help="Upload a PDF file to process"
    )

    if uploaded_file:
        # File details card
        st.markdown(f"""
            <div class="feature-card">
                <h3 style="font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem;">📄 File Details</h3>
                <p>Filename: {uploaded_file.name}</p>
                <p>Size: {uploaded_file.size / 1024:.2f} KB</p>
                <p>Type: {uploaded_file.type}</p>
            </div>
        """, unsafe_allow_html=True)

        # Process button
        if st.button("🚀 Process PDF", type="primary"):
            with st.spinner("Processing your PDF... Please wait"):
                try:
                    temp_path = save_uploaded_file(uploaded_file)
                    if temp_path:
                        excel_path = process_pdf(temp_path)
                        
                        if excel_path and os.path.exists(excel_path):
                            df = pd.read_excel(excel_path)
                            
                            st.success("✅ PDF processed successfully!")
                            
                            st.markdown("""
                                <div class="feature-card">
                                    <h3 style="font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem;">
                                        📊 Preview of Processed Content
                                    </h3>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            st.dataframe(
                                df.head(10),
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            with open(excel_path, "rb") as file:
                                excel_data = file.read()
                                output_filename = f"{uploaded_file.name.replace('.pdf', '_processed.xlsx')}"
                                
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.info("💡 File will automatically download in 3 seconds...")
                                with col2:
                                    st.download_button(
                                        label="📥 Download Excel",
                                        data=excel_data,
                                        file_name=output_filename,
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        key='manual_download',
                                        on_click=lambda: st.session_state.update({'manual_download': True})
                                    )
                                
                                st.markdown(create_auto_download_button(excel_data, output_filename), unsafe_allow_html=True)
                            
                            try:
                                os.remove(temp_path)
                                os.remove(excel_path)
                            except Exception as e:
                                logger.error(f"Error cleaning up files: {str(e)}")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    logger.error(f"Processing error: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("""
        <div style="margin-top: 4rem; text-align: center; opacity: 0.7;">
            <p>Made with ❤️ for PDF processing</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()