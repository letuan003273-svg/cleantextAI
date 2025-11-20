import streamlit as st
import re
import openai

# --- Cấu hình trang ---
st.set_page_config(page_title="AI Text Humanizer", page_icon="✍️", layout="centered")

# --- Hàm xử lý làm sạch mã (Logic cũ) ---
def clean_openai_text(text):
    if not text: return ""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text) # Xóa in đậm
    text = re.sub(r'\*(.*?)\*', r'\1', text)     # Xóa in nghiêng
    text = re.sub(r'_(.*?)_', r'\1', text)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE) # Xóa tiêu đề
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL) # Xóa khối code
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text) # Xóa link
    return text.strip()

# --- Hàm gọi AI để viết lại (Logic mới) ---
def humanize_text(text, api_key, tone="bình thường"):
    if not api_key:
        return "⚠️ Vui lòng nhập OpenAI API Key ở thanh bên trái để dùng tính năng này."
    
    client = openai.OpenAI(api_key=api_key)
    
    # Prompt yêu cầu viết lại tự nhiên
    prompt_instruction = (
        "Bạn là một biên tập viên chuyên nghiệp. Hãy viết lại đoạn văn bản sau đây "
        "bằng tiếng Việt với giọng văn tự nhiên, gần gũi như con người viết. "
        "Tránh dùng các từ sáo rỗng, lặp lại hoặc cấu trúc câu máy móc thường thấy của AI. "
        "Giữ nguyên ý chính nhưng thay đổi cấu trúc câu cho linh hoạt."
    )
    
    if tone == "hài hước":
        prompt_instruction += " Hãy thêm một chút giọng điệu hài hước, dí dỏm."
    elif tone == "nghiêm túc":
        prompt_instruction += " Hãy dùng giọng văn trang trọng, chuyên nghiệp."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Hoặc gpt-4 nếu bạn có quyền truy cập
            messages=[
                {"role": "system", "content": prompt_instruction},
                {"role": "user", "content": text}
            ],
            temperature=0.7 # Độ sáng tạo cao hơn để bớt giống máy
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Lỗi: {str(e)}"

# --- Giao diện người dùng (UI) ---
st.title("✍️ AI Text Cleaner & Humanizer")
st.markdown("Công cụ loại bỏ định dạng Markdown và viết lại văn bản cho tự nhiên hơn.")

# Sidebar: Cấu hình API
with st.sidebar:
    st.header("⚙️ Cấu hình")
    api_key = st.text_input("OpenAI API Key", type="password", help="Cần API Key để dùng tính năng viết lại.")
    st.info("Nếu chưa có, hãy lấy key tại platform.openai.com")
    st.divider()
    st.write("Chế độ viết lại cần API Key, chế độ làm sạch thì miễn phí.")

# Khu vực nhập liệu
input_text = st.text_area("Dán văn bản gốc vào đây:", height=200, placeholder="Dán văn bản từ ChatGPT...")

# Tabs chuyển đổi chức năng
tab1, tab2 = st.tabs(["🧹 Chỉ làm sạch (Clean)", "✨ Viết lại (Humanize)"])

# --- TAB 1: CHỈ LÀM SẠCH ---
with tab1:
    st.caption("Chế độ này chỉ loại bỏ các ký tự *, #, link... giữ nguyên nội dung.")
    # Nút bấm chuyển phía dưới (Action Button)
    if st.button("🚀 Làm sạch ngay", key="btn_clean"):
        if input_text:
            cleaned = clean_openai_text(input_text)
            st.success("Đã xử lý xong!")
            st.text_area("Kết quả:", value=cleaned, height=300)
        else:
            st.warning("Vui lòng nhập văn bản trước.")

# --- TAB 2: VIẾT LẠI GIỌNG NGƯỜI ---
with tab2:
    st.caption("Chế độ này dùng AI để diễn giải lại ý giúp tránh các công cụ phát hiện AI.")
    
    # Tùy chọn giọng văn
    tone_option = st.radio("Chọn giọng văn:", ["Bình thường", "Hài hước", "Nghiêm túc"], horizontal=True)
    
    # Nút bấm chuyển phía dưới
    if st.button("🚀 Viết lại tự nhiên", key="btn_humanize"):
        if input_text:
            # Bước 1: Làm sạch trước
            pre_cleaned = clean_openai_text(input_text)
            
            # Bước 2: Gọi AI viết lại
            with st.spinner("Đang suy nghĩ và viết lại..."):
                humanized = humanize_text(pre_cleaned, api_key, tone_option.lower())
            
            if "⚠️" in humanized or "Lỗi" in humanized:
                st.error(humanized)
            else:
                st.success("Đã viết lại thành công!")
                st.text_area("Kết quả:", value=humanized, height=300)
        else:
            st.warning("Vui lòng nhập văn bản trước.")

st.markdown("---")
st.caption("Lưu ý: Không có công cụ nào đảm bảo vượt qua 100% AI Detector, nhưng việc viết lại giọng tự nhiên sẽ giúp ích rất nhiều.")
