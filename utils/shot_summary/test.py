import google.generativeai as genai
from api_keys import API_KEYS

API_KEY = "AIzaSyBYTUj9P32XGOoF4WJ-X4jldoX_Yr0fDII"

genai.configure(api_key=API_KEY)

video = genai.upload_file(
    path="/mmlabworkspace/Students/visedit/AIC2024/Utils/shot_summary/scene.mp4"
)

prompt = """
viết đoạn mô tả nội dung chính và từng chi tiết nhỏ nhất có trong video
"""

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

respond = model.generate_content([prompt, video])

print(respond.text)
"""
Video ghi lại cảnh một nhóm người đang cố gắng di chuyển trong dòng nước lũ trên đường tại xã Hà Linh, huyện Hương Khê, Hà Tĩnh. Mưa lũ đã cuốn trôi 3 người tại đây.  

Chi tiết video:

* **Nước lũ**: Dòng nước lũ đục ngầu, chảy xiết, ngập đến gần đầu gối người lớn.
* **Nhóm người**: Có 2 nhóm người đang cố gắng di chuyển trong dòng nước lũ: 
    * Nhóm 3 người phụ nữ đang dắt díu nhau lội nước. 
    * Nhóm 3 người (2 người lớn và 1 trẻ em) đang ngồi trên một chiếc xe máy, được một người đàn ông dắt bộ.
* **Phương tiện**: 
    * Một chiếc xe tải màu xanh đang bị chết máy, mắc kẹt trong dòng nước lũ. 
    * Bên phải, xa xa là một chiếc xe màu trắng đang di chuyển rất khó khăn.
* **Môi trường**: Cây cối hai bên đường nghiêng ngả vì gió, trời mưa to.
* **Thông tin hiển thị trên màn hình**:
    * Góc trái màn hình: Logo chương trình "60 giây", số thứ tự tin 18-3.
    * Góc phải màn hình: Logo đài truyền hình HTV9HD, thời gian phát sóng 06:31:07.
    * Phía dưới màn hình: Dòng chữ "Hà Tĩnh: Mưa lũ lớn liên nhanh khiến 3 người bị nước cuốn trôi".

Video cho thấy sự nguy hiểm của mưa lũ, đồng thời cho thấy nỗ lực của người dân trong việc ứng phó với thiên tai.
"""

print(respond.usage_metadata)
"""
prompt_token_count: 2085
candidates_token_count: 378
total_token_count: 2463
"""
