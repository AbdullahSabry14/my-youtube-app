# import streamlit as st

# # إعدادات الصفحة
# st.set_page_config(page_title="تجرية الأتمتة", page_icon="🤖")

# st.title("🚀 مرحباً بك في موقعك الأول!")
# st.subheader("هذا الموقع يعمل بواسطة بايثون بالكامل")

# # إدخال نص
# user_name = st.text_input("ما هو اسمك؟")

# if user_name:
#     st.success(f"أهلاً بك يا {user_name}! الموقع شغال 100%")

# # زر بسيط
# if st.button("اضغط هنا لتجربة التفاعل"):
#     st.balloons() # حركة احتفالية
#     st.info("الآن تخيل أن هذا الزر هو الذي سيرفع الفيديو ليوتيوب!")


import streamlit as st
import datetime
import time
    
# إعدادات الواجهة لتناسب الموبايل (RTL)
st.markdown("""<style> .stApp { direction: RTL; text-align: right; } </style>""", unsafe_allow_html=True)

st.title("🤖 مساعد أبو الصبري الذكي")
st.subheader("لوحة تحكم أتمتة يوتيوب")

# 1. قسم البيانات
with st.container():
    title = st.text_input("📝 عنوان الفيديو")
    description = st.text_area("📄 وصف الفيديو")
    
# 2. قسم الملفات
video_file = st.file_uploader("🎬 اختر الفيديو من الاستوديو", type=['mp4', 'mov'])
thumbnail = st.file_uploader("🖼️ اختر الصورة المصغرة", type=['jpg', 'png'])

# 3. قسم الوقت (الجدولة)
scheduled_date = st.date_input("📅 تاريخ الرفع", datetime.date.today())
scheduled_time = st.time_input("⏰ وقت الرفع")

# 4. زر التنفيذ
if st.button("🚀 اعتمد العملية وجدول الرفع"):
    if video_file and title:
        st.success(f"تم استلام الفيديو: {title}")
        st.info(f"سيتم الرفع بتاريخ {scheduled_date} الساعة {scheduled_time}")
        
        # هنا سنضع كود الـ YouTube API لاحقاً
        # حالياً سنحفظ الملف مؤقتاً على السيرفر
        with open("uploaded_video.mp4", "wb") as f:
            f.write(video_file.read())
    else:
        st.error("الرجاء التأكد من رفع الفيديو وكتابة العنوان")