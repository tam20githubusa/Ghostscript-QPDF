import streamlit as st
import subprocess
import os
import re

st.set_page_config(page_title="PDF 极致瘦身与防伪全自动面板", layout="centered")

st.title("🔬 PDF 极致瘦身与指纹防伪洗刷控制台")
st.markdown("通过云端/本地后端直接唤起 **Ghostscript**，强锁 PDF-1.7 并结合【字体加号前缀硬洗】实现终极无痕。")

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
    
    raw_bytes = uploaded_file.getbuffer().nbytes
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    if st.button("🚀 开始终极无痕重构（强洗加号前缀）", type="primary"):
        with st.spinner("正在强力逆转字体流基因... 请稍候..."):
            try:
                # ==========================================
                # 步骤 A：唤起 Ghostscript 压缩并重构
                # ==========================================
                # 恢复为标准的子集化压缩，先把体积压到最小，后续用 Python 手动剥离加号
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
                # 步骤 B：纯内存二进制硬洗 (签名 + 字体加号前缀)
                # ==========================================
                with open(output_gs_path, "rb") as f:
                    pdf_data = f.read()

                # 1. 刺杀 Ghostscript 相关所有文本特征
                targets = [b"GPL Ghostscript 10.05.1", b"GPL Ghostscript 10.05", b"GPL Ghostscript", b"Ghostscript"]
                for target in targets:
                    if target in pdf_data:
                        t_len = len(target)
                        if custom_producer.strip() == "":
                            replacement = b" " * t_len
                        else:
                            p_bytes = custom_producer.encode('latin1')
                            replacement = p_bytes[:t_len] if len(p_bytes) >= t_len else p_bytes + b" " * (t_len - len(p_bytes))
                        pdf_data = pdf_data.replace(target, replacement)

                # 2. 核心绝杀：使用正则在二进制中剔除 `XXXXXX+` 字体前缀
                # PDF底层字体名通常以斜杠开头，如 /AAAAAA+SimSun，匹配 6位大写字母+加号
                def remove_font_prefix(match):
                    # match.group(0) 是类似于 b'/ABCDEF+' 的数据
                    # 我们把它替换为同等长度的空格加斜杠，维持二进制文件指针完全对齐，绝不破坏物理结构
                    matched_str = match.group(0)
                    return b"/" + b" " * (len(matched_str) - 1)

                # 匹配 / 后面跟着 6 个大写字母，再跟着一个加号的二进制特征
                pdf_data = re.sub(rb'/[A-Z]{6}\+', remove_font_prefix, pdf_data)

                # 将彻底洗净的二进制数据覆写回成品
                with open(output_gs_path, "wb") as f:
                    f.write(pdf_data)

                # ==========================================
                # 4. 交付成品与数据反馈
                # ==========================================
                if os.path.exists(output_gs_path):
                    clean_bytes = os.path.getsize(output_gs_path)
                    saved_ratio = (1 - (clean_bytes / raw_bytes)) * 100
                    
                    st.success("✨ 终极去痕重构结束！加号前缀与引擎特征已被物理性蒸发。")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("原始文件大小", format_bytes(raw_bytes))
                    col2.metric("优化去痕后大小", format_bytes(clean_bytes))
                    col3.metric("整体瘦身率", f"{saved_ratio:.1f}%")
                    
                    with open(output_gs_path, "rb") as file:
                        st.download_button(
                            label="📥 下载终极无瑕疵 PDF 成品",
                            data=file,
                            file_name=f"clean_{uploaded_file.name}",
                            mime="application/pdf"
                        )
            
            except Exception as e:
                st.error(f"系统发生未预料异常: {str(e)}")
            
            finally:
                if os.path.exists(input_path): os.remove(input_path)
