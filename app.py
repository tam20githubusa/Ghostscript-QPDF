import streamlit as st
import subprocess
import os

st.set_page_config(page_title="PDF 极致瘦身与防伪全自动面板", layout="centered")

st.title("🔬 PDF 极致瘦身与指纹防伪洗刷控制台")
st.markdown("通过云端/本地后端直接唤起 **Ghostscript**，强锁 PDF-1.7 并结合【二进制明文重洗】彻底抠除底层痕迹。")

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
        
    if st.button("🚀 开始联合作战（重构 + 字节流硬清除）", type="primary"):
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
                    "-dEmbedAllFonts=true", "-dSubsetFonts=false",
                    f"-sOutputFile={output_gs_path}", input_path
                ]
                
                result_gs = subprocess.run(gs_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if not os.path.exists(output_gs_path):
                    st.error(f"Ghostscript 压缩失败！错误日志:\n{result_gs.stderr}")
                    st.stop()
                    
                # ==========================================
                # 步骤 B：【核心必杀技】Python 纯内存二进制明文替换
                # ==========================================
                with open(output_gs_path, "rb") as f:
                    pdf_data = f.read()

                # 转换目标签名的各种可能形态为二进制字节流
                targets = [
                    b"GPL Ghostscript 10.05.1",
                    b"GPL Ghostscript 10.05",
                    b"GPL Ghostscript",
                    b"Ghostscript"
                ]

                # 设定替换后的伪装物（必须保持等长，否则PDF索引会错位崩溃）
                # 如果用户留空，用等长空格物理覆盖；如果用户写了，用伪装字符等长截断或填充
                for target in targets:
                    if target in pdf_data:
                        t_len = len(target)
                        if custom_producer.strip() == "":
                            # 用完全等长的纯空格抹平它
                            replacement = b" " * t_len
                        else:
                            # 用自定义字符填充，长了就截断，短了就补空格，必须维持 t_len 长度不变
                            p_bytes = custom_producer.encode('latin1')
                            if len(p_bytes) >= t_len:
                                replacement = p_bytes[:t_len]
                            else:
                                replacement = p_bytes + b" " * (t_len - len(p_bytes))
                        
                        # 执行二进制暴力替换
                        pdf_data = pdf_data.replace(target, replacement)

                # 将洗得干干净净的二进制数据重新覆写回文件
                with open(output_gs_path, "wb") as f:
                    f.write(pdf_data)

                # ==========================================
                # 4. 交付成品与数据反馈
                # ==========================================
                if os.path.exists(output_gs_path):
                    clean_bytes = os.path.getsize(output_gs_path)
                    saved_ratio = (1 - (clean_bytes / raw_bytes)) * 100
                    
                    st.success("✨ 终极去痕重构结束！已强制从二进制底层数据流中擦除 Ghostscript 印记。")
                    
                    # 📊 数据面板显示
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
