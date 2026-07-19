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

def format_bytes(size_in_bytes):
    if size_in_bytes == 0: return '0 Bytes'
    for unit in ['Bytes', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024

# 3. 执行核心逻辑
if uploaded_file is not None:
    input_path = "input_temp.pdf"
    output_gs_path = "output_gs.pdf"
    
    # 获取原始大小
    raw_bytes = uploaded_file.getbuffer().nbytes
    
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
                
                result_gs = subprocess.run(gs_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if not os.path.exists(output_gs_path):
                    st.error(f"Ghostscript 压缩失败！错误日志:\n{result_gs.stderr}")
                    st.stop()
                    
                # ==========================================
                # 步骤 B：【地毯式轰炸】ExifTool 彻底粉碎 XML 元数据流
                # ==========================================
                # 不仅删除单独的 Producer，而是将底层的 XMP 字典、XML 描述块直接物理注销
                if custom_producer.strip() == "":
                    exif_cmd = [
                        "exiftool",
                        "-all=",                 # 核心：直接斩断并清空所有元数据字典、XML数据流
                        "-pdf:all=",             # 清空 PDF 专属内部标签
                        "-xmp:all=",             # 彻底粉碎隐藏在 XML 流里的特征
                        "-Producer=", 
                        "-Creator=", 
                        "-CreatorTool=", 
                        "-history=",
                        "-overwrite_original", 
                        output_gs_path
                    ]
                else:
                    exif_cmd = [
                        "exiftool",
                        "-all=",                 # 先清除干净所有隐藏流
                        "-pdf:all=",
                        "-xmp:all=",
                        f"-Producer={custom_producer}", # 再反向写入你指定的伪装签名
                        "-Creator=", 
                        "-CreatorTool=", 
                        "-history=",
                        "-overwrite_original", 
                        output_gs_path
                    ]
                
                # 执行地毯式清理
                result_exif = subprocess.run(exif_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                # ==========================================
                # 4. 交付成品与数据反馈
                # ==========================================
                if os.path.exists(output_gs_path):
                    clean_bytes = os.path.getsize(output_gs_path)
                    saved_ratio = (1 - (clean_bytes / raw_bytes)) * 100
                    
                    st.success("✨ 联合作战完美结束！底层的影子元数据与压缩流已被彻底解构。")
                    
                    # 📊 明确显示压缩完的文件大小数据面板
                    col1, col2, col3 = st.columns(3)
                    col1.metric("原始文件大小", format_bytes(raw_bytes))
                    col2.metric("优化去痕后大小", format_bytes(clean_bytes))
                    col3.metric("整体瘦身率", f"{saved_ratio:.1f}%")
                    
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
                if os.path.exists(input_path): os.remove(input_path)
