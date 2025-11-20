import streamlit as st
import re
import google.generativeai as genai

# --- Cấu hình trang ---
st.set_page_config(page_title="AI Text Humanizer (Gemini)", page_icon="✨", layout="centered")

# --- Hàm xử lý làm sạch mã ---
def clean_openai_text(text):
    if not text: return ""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    return text.strip()

# --- Hàm gọi Gemini API ---
def humanize_text_gemini(text, api_key, tone="bình thường"):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    instruction = (
        "Bạn là một biên tập viên tiếng Việt chuyên nghiệp. "
        "Nhiệm vụ: Viết lại đoạn văn bản dưới đây sao cho giọng văn tự nhiên, gần gũi như người thật viết. "
        "Yêu cầu: Loại bỏ các từ ngữ sáo rỗng, máy móc. Giữ nguyên ý chính nhưng thay đổi cấu trúc câu linh hoạt.\n"
    )
    
    if tone == "hài hước":
        instruction += "Thêm giọng điệu hài hước, dí dỏm.\n"
    elif tone == "nghiêm túc":
        instruction += "Dùng giọng văn trang trọng, chuyên nghiệp.\n"
    
    full_prompt = f"{instruction}\n---\nVăn bản gốc:\n{text}"

    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Lỗi khi gọi Gemini: {str(e)}"

# --- Hàm hiển thị kết quả (Tái sử dụng để code gọn hơn) ---
def show_result_area(result_text, filename_prefix):
    """Hàm hiển thị vùng kết quả bao gồm Text area, nút Copy và Download"""
    
    st.markdown("### 🎉 Kết quả:")
    
    # 1. Hiển thị để đọc (Text Area)
    st.text_area("Đọc và chỉnh sửa:", value=result_text, height=250)
    
    # Chia 2 cột cho nút Copy và Download
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        # 2. Vùng sao chép nhanh (Mẹo dùng st.code để có nút copy)
        st.info("👇 Bấm vào góc phải ô dưới để Copy nhanh:")
        st.code(result_text, language=None) 

    with col_b:
        # 3. Nút tải xuống
        st.write("👇 Hoặc tải về máy:")
        st.download_button(
            label="📥 Tải xuống file .txt",
            data=result_text,
            file_name=f"{filename_prefix}.txt",
            mime="text/plain",
            use_container_width=True # Làm nút rộng ra cho đẹp
        )

# --- Giao diện chính ---
st.title("✨ AI Text Cleaner & Humanizer")

# --- XỬ LÝ API KEY ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    st.sidebar.success("✅ Gemini API Key đã kích hoạt.")
else:
    st.sidebar.warning("⚠️ Chưa cấu hình Secrets.")
    api_key = st.sidebar.text_input("Nhập Gemini API Key", type="password")

# Khu vực nhập liệu
input_text = st.text_area("Dán văn bản gốc vào đây:", height=150, placeholder="Dán văn bản cần xử lý...")

# Tabs
tab1, tab2 = st.tabs(["🧹 Chỉ làm sạch (Clean)", "✨ Viết lại (Humanize)"])

# --- TAB 1: LÀM SẠCH ---
with tab1:
    if st.button("🚀 Làm sạch ngay", key="btn_clean"):
        if input_text:
            cleaned = clean_openai_text(input_text)
            # Gọi hàm hiển thị kết quả
            show_result_area(cleaned, "van_ban_sach")
        else:
            st.warning("Vui lòng nhập văn bản trước.")

# --- TAB 2: VIẾT LẠI ---
with tab2:
    tone_option = st.radio("Chọn giọng văn:", ["Bình thường", "Hài hước", "Nghiêm túc"], horizontal=True)
    
    if st.button("🚀 Viết lại bằng Gemini", key="btn_humanize"):
        if not input_text:
            st.warning("Vui lòng nhập văn bản trước.")
        elif not api_key:
            st.error("Thiếu API Key.")
        else:
            pre_cleaned = clean_openai_text(input_text)
            with st.spinner("Gemini đang viết lại..."):
                humanized = humanize_text_gemini(pre_cleaned, api_key, tone_option.lower())
            
            if "Lỗi" in humanized:
                st.error(humanized)
            else:
                # Gọi hàm hiển thị kết quả
                show_result_area(humanized, "van_ban_humanized")

st.markdown("---")
st.caption("App powered by Google Gemini")
