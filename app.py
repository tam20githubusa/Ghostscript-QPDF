import streamlit as st
import subprocess
import os
import time

st.set_page_config(page_title="PDF Optimizer Pro", page_icon="📄")

st.title("📄 Professional PDF Optimizer")
st.caption("Powered by Ghostscript & QPDF | Cloud Infrastructure")

# --- Function: Ghostscript (Structure Clean) ---
def run_ghostscript(input_path, output_path):
    cmd = [
        "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/default", # Keep original quality
        "-dColorImageResolution=600", "-dGrayImageResolution=600",
        "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={output_path}", input_path
    ]
    subprocess.run(cmd, check=True)

# --- Function: QPDF (Lossless & Linearize) ---
def run_qpdf(input_path, output_path):
    cmd = [
        "qpdf", "--linearize", "--optimize-images",
        "--min-version=1.5", input_path, output_path
    ]
    subprocess.run(cmd, check=True)

# --- UI Sidebar ---
st.sidebar.header("Optimization Settings")
mode = st.sidebar.radio(
    "Select Mode:",
    ("Lossless (QPDF)", "Deep Clean (Ghostscript)"),
    index=1  # 这里将默认值改为了 Ghostscript
)

# --- Main Logic ---
uploaded_file = st.file_uploader("Upload your PDF (Max 200MB)", type="pdf")

if uploaded_file is not None:
    # 1. Save uploaded file to a temporary location
    input_filename = "temp_input.pdf"
    output_filename = f"optimized_{mode.split()[0].lower()}.pdf"
    
    with open(input_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.info(f"Original Size: {len(uploaded_file.getbuffer())/1024:.2f} KB")

    if st.button("Start Optimization"):
        with st.spinner(f"Running {mode}..."):
            try:
                start_time = time.time()
                
                if "QPDF" in mode:
                    run_qpdf(input_filename, output_filename)
                else:
                    run_ghostscript(input_filename, output_filename)
                
                duration = time.time() - start_time
                
                # 2. Results
                if os.path.exists(output_filename):
                    new_size = os.path.getsize(output_filename)
                    st.success(f"Done in {duration:.2f}s!")
                    st.metric("New Size", f"{new_size/1024:.2f} KB", 
                              delta=f"{(new_size - len(uploaded_file.getbuffer()))/1024:.2f} KB")
                    
                    # 3. Download Button
                    with open(output_filename, "rb") as file:
                        st.download_button(
                            label="📥 Download Optimized PDF",
                            data=file,
                            file_name=output_filename,
                            mime="application/pdf"
                        )
                    
                    # Cleanup
                    os.remove(input_filename)
                    os.remove(output_filename)
            except Exception as e:
                st.error(f"Error during processing: {e}")
