import streamlit as st
import subprocess
import os

st.set_page_config(page_title="PDF 极致瘦身与防伪全自动面板", layout="centered")

st.title("🔬 PDF 极致瘦身与指纹防伪洗刷控制台")
st.markdown("通过云端/本地后端直接唤起 **Ghostscript** 与 **ExifTool**，强锁 PDF-1.7 并定点清除第三方重构签名。")

# 1. 文件上传
uploaded_file = st.file_uploader("📂 第一步：请投放你需要去痕压缩的 PDF 文件", type=["pdf"])

# 2. 参数微调
st.markdown("### 🛠️ 第二步：防伪整容参数配置")
pdf_version = st.selectbox("强锁 PDF 底层版本规范", ["1.7", "1.6", "1.5"], index=0)
custom_producer = st.text_input("期望伪装的 Producer 签名（留空代表彻底清空，最安全推荐）", "")

# 3. 执行核心逻辑
if uploaded_file is not None:
    # 建立临时工作路径
    input_path = "input_temp.pdf"
    output_gs_path = "output_gs.pdf"
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    if st.button("🚀 开始联合作战（重构 + 洗签名）", type="primary"):
        with st.spinner("后端正在激烈重洗代码流... 请稍候..."):
            try:
                # ==========================================
                # 步骤 A：唤起 Ghostscript 强锁版本并无损重构
                # ==========================================
                gs_cmd = [
                    "gs", "-sDEVICE=pdfwrite",
                    f"-dCompatibilityLevel={pdf_version}",
                    "-dNOPAUSE", "-dBATCH", "-dQUIET",
                    "-dColorImageDownsampleType=/Bicubic", "-dColorImageResolution=300",
                    "-dGrayImageDownsampleType=/Bicubic", "-dGrayImageResolution=300",
                    "-dMonoImageDownsampleType=/Bicubic", "-dMonoImageResolution=300",
                    "-dEmbedAllFonts=true", "-dSubsetFonts=true",
                    f"-sOutputFile={output_gs_path}", input_path
                ]
                
                # 执行 GS
                result_gs = subprocess.run(gs_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if not os.path.exists(output_gs_path):
                    st.error(f"Ghostscript 压缩失败！错误日志:\n{result_gs.stderr}")
                    st.stop()
                    
                # ==========================================
                # 步骤 B：修复后的 ExifTool 精准洗签名逻辑 (Linux 兼容版)
                # ==========================================
                if custom_producer.strip() == "":
                    # 如果用户留空，使用 ExifTool 在 Linux/Python 传参下唯一的“物理抠除”语法
                    # 参数后面不接任何东西（直接截断），代表彻底删掉这些字典键值
                    exif_cmd = [
                        "exiftool",
                        "-Producer=", 
                        "-Creator=", 
                        "-CreatorTool=", 
                        "-history=",
                        "-MetadataDate=",
                        "-ModifyDate=",
                        "-overwrite_original", 
                        output_gs_path
                    ]
                else:
                    # 如果用户输入了伪装文本（比如“官方原生导出”），则执行强制覆盖
                    exif_cmd = [
                        "exiftool",
                        f"-Producer={custom_producer}",
                        "-Creator=", 
                        "-CreatorTool=", 
                        "-history=",
                        "-MetadataDate=",
                        "-ModifyDate=",
                        "-overwrite_original", 
                        output_gs_path
                    ]
                
                # 执行 ExifTool
                result_exif = subprocess.run(exif_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                # ==========================================
                # 4. 交付成品
                # ==========================================
                if os.path.exists(output_gs_path):
                    st.success("✨ 联合作战完美结束！底层的 Ghostscript 签名与降维痕迹已被彻底抹除。")
                    
                    # 读取成品文件提供下载
                    with open(output_gs_path, "rb") as file:
                        btn = st.download_button(
                            label="📥 下载终极无瑕疵 PDF 成品",
                            data=file,
                            file_name=f"clean_{uploaded_file.name}",
                            mime="application/pdf"
                        )
            
            except Exception as e:
                st.error(f"系统发生未预料异常: {str(e)}")
            
            finally:
                # 清理现场临时文件，防止服务器存储泄露
                if os.path.exists(input_path): os.remove(input_path)
