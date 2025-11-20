import streamlit as st
import re
import google.generativeai as genai

# --- Cấu hình trang ---
st.set_page_config(page_title="AI Text Humanizer (Gemini)", page_icon="✨", layout="centered")

# --- Hàm xử lý làm sạch mã (Logic Regex giữ nguyên) ---
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

# --- Hàm gọi Gemini API để viết lại ---
def humanize_text_gemini(text, api_key, tone="bình thường"):
    # Cấu hình API Key
    genai.configure(api_key=api_key)
    
    # Chọn model (gemini-2.5-flash chạy nhanh và hiệu quả cho text)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Xây dựng câu lệnh (Prompt)
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

# --- Giao diện người dùng (UI) ---
st.title("✨ AI Text Cleaner & Humanizer")
st.caption("Sử dụng sức mạnh của Google Gemini")

# --- XỬ LÝ API KEY TỰ ĐỘNG (Secrets) ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    st.sidebar.success("✅ Gemini API Key đã được kích hoạt.")
else:
    st.sidebar.warning("⚠️ Chưa cấu hình Secrets.")
    api_key = st.sidebar.text_input("Nhập Gemini API Key", type="password")
    st.sidebar.markdown("[Lấy API Key tại đây](https://aistudio.google.com/app/apikey)")

# Khu vực nhập liệu
input_text = st.text_area("Dán văn bản gốc vào đây:", height=200, placeholder="Dán văn bản từ ChatGPT/Gemini...")

# Tabs chuyển đổi
tab1, tab2 = st.tabs(["🧹 Chỉ làm sạch (Clean)", "✨ Viết lại (Humanize)"])

# --- TAB 1: CHỈ LÀM SẠCH ---
with tab1:
    if st.button("🚀 Làm sạch ngay", key="btn_clean"):
        if input_text:
            cleaned = clean_openai_text(input_text)
            st.text_area("Kết quả:", value=cleaned, height=300)
        else:
            st.warning("Vui lòng nhập văn bản trước.")

# --- TAB 2: VIẾT LẠI (DÙNG GEMINI) ---
with tab2:
    tone_option = st.radio("Chọn giọng văn:", ["Bình thường", "Hài hước", "Nghiêm túc"], horizontal=True)
    
    if st.button("🚀 Viết lại bằng Gemini", key="btn_humanize"):
        if not input_text:
            st.warning("Vui lòng nhập văn bản trước.")
        elif not api_key:
            st.error("Thiếu API Key. Vui lòng nhập Key.")
        else:
            pre_cleaned = clean_openai_text(input_text)
            with st.spinner("Gemini đang viết lại..."):
                humanized = humanize_text_gemini(pre_cleaned, api_key, tone_option.lower())
            
            if "Lỗi" in humanized:
                st.error(humanized)
            else:
                st.success("Đã viết lại thành công!")
                st.text_area("Kết quả:", value=humanized, height=300)

st.markdown("---")
st.caption("App sử dụng model gemini-1.5-flash")
