import streamlit as st
import re

# --- Cấu hình trang ---
st.set_page_config(
    page_title="AI Text Cleaner",
    page_icon="🧹",
    layout="centered"
)

# --- Hàm xử lý làm sạch văn bản ---
def clean_openai_text(text):
    """
    Hàm này loại bỏ các định dạng Markdown thường gặp từ OpenAI.
    """
    if not text:
        return ""
    
    # 1. Loại bỏ in đậm đậm (**text**)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    
    # 2. Loại bỏ in nghiêng (*text* hoặc _text_)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    
    # 3. Loại bỏ tiêu đề (### Header)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    
    # 4. Loại bỏ khối mã (```code```) - Tùy chọn: có thể muốn giữ lại hoặc xóa hẳn
    # Ở đây tôi sẽ giữ nội dung bên trong nhưng xóa dấu ```
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL) # Xóa cả khối mã (nếu muốn giữ nội dung, sửa logic này)
    text = re.sub(r'`(.*?)`', r'\1', text) # Code inline
    
    # 5. Loại bỏ link markdown [text](url) -> chỉ giữ lại text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    
    return text.strip()

# --- Giao diện người dùng (UI) ---
st.title("🧹 Công cụ làm sạch văn bản AI")
st.write("Dán văn bản từ ChatGPT vào bên dưới để loại bỏ các ký tự định dạng (Markdown).")

# Cột chia giao diện
col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 Văn bản gốc")
    input_text = st.text_area("Dán văn bản vào đây:", height=300, placeholder="Ví dụ: Dưới đây là **kết quả** của bạn...")

with col2:
    st.subheader("📤 Văn bản đã làm sạch")
    
    if input_text:
        cleaned_text = clean_openai_text(input_text)
        st.text_area("Kết quả:", value=cleaned_text, height=300)
        
        # Nút tải xuống
        st.download_button(
            label="Tải xuống file .txt",
            data=cleaned_text,
            file_name="van_ban_sach.txt",
            mime="text/plain"
        )
    else:
        st.info("Đang chờ văn bản đầu vào...")

# Footer
st.markdown("---")
st.caption("Được xây dựng bằng Python & Streamlit")
