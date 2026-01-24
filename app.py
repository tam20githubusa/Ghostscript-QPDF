import streamlit as st
import subprocess
import os

# 侧边栏导航：切换聊天室和 PDF 工具
st.sidebar.title("🛠️ Tools Box")
app_mode = st.sidebar.selectbox("Choose Module", ["Global Chat", "PDF Slimmer"])

if app_mode == "PDF Slimmer":
    st.title("📄 Smart PDF Slimmer")
    st.info("Best for: Removing hidden bloat and font subsets while keeping quality.")
    
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    
    if uploaded_file:
        input_path = "input_temp.pdf"
        output_path = "cleaned_high_quality.pdf"
        
        with open(input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 强制使用你测试成功的方案 A (600dpi + Structure Clean)
        if st.button("Deep Clean (Ghostscript)"):
            with st.spinner("Purging redundant data..."):
                cmd = [
                    "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
                    "-dPDFSETTINGS=/default",
                    "-dColorImageResolution=600", "-dGrayImageResolution=600",
                    "-dNOPAUSE", "-dQUIET", "-dBATCH",
                    f"-sOutputFile={output_path}", input_path
                ]
                subprocess.run(cmd)
                
                new_size = os.path.getsize(output_path)
                st.metric("Optimization Result", f"{new_size/1024:.2f} KB")
                
                with open(output_path, "rb") as f:
                    st.download_button("📥 Download 532KB Version", f, file_name="slim_pro.pdf")
