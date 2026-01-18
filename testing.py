import streamlit as st
import datetime
import time
import requests
import pickle
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- 1. إعدادات الصفحة (تحسين العرض للجوال) ---
st.set_page_config(page_title="المساعد الذكي", page_icon="🤖", layout="wide")

# إخفاء قائمة Streamlit العلوية لتقليل العجقة
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {width: 100%; border-radius: 10px; height: 3em;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. تهيئة الذاكرة ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1, 'v_file': None, 't_file': None,
        'v_title': "", 'v_desc': "", 'tags': [], 'show_err': False
    })

# --- الدوال (نفس منطقك الأصلي) ---
def send(t):
    sid = "ACe0557f10e02c653e115d0810818d2ccc"
    tok = "c480f9562d1e76e279961bbb46c8ee49"
    try:
        requests.post(f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
                      data={"From": "whatsapp:+14155238886", "To": "whatsapp:+970595859974", "Body": t},
                      auth=(sid, tok))
    except: pass

def move(target):
    s = st.session_state
    if target > s.step:
        if s.step == 1 and not s.v_file: s.show_err = True; return
        if s.step == 2 and not s.t_file: s.show_err = True; return
        if s.step == 3 and not s.v_title.strip(): s.show_err = True; return
        if s.step == 4 and not s.v_desc.strip(): s.show_err = True; return
    s.show_err = False
    s.step = target
    st.rerun()

# --- 3. الشاشة الجانبية (مختصرة جداً) ---
with st.sidebar:
    st.markdown("### 🛠️ الإعدادات")
    if st.button("🗑️ مسح كل شيء"):
        for k in ['v_file','t_file','v_title','v_desc','tags']: 
            st.session_state[k] = None if 'file' in k else ("" if k != 'tags' else [])
        st.session_state.step = 1
        st.rerun()
    st.info(f"الخطوة الحالية: {st.session_state.step}/6")

# --- 4. العناوين المختصرة ---
st.markdown("<h2 style='text-align: center; color: #FF0000;'>SABRY TUBE</h2>", unsafe_allow_html=True)
st.progress((st.session_state.step - 1) / 5.0)

# --- 5. منطق الصفحات (كل الأزرار زحفت لليمين) ---
placeholder = st.container()

with placeholder:
    if st.session_state.step == 1:
        st.subheader("🎬 اختر الفيديو")
        v = st.file_uploader("", type=['mp4', 'mov'])
        if v: st.session_state.v_file = v

    elif st.session_state.step == 2:
        st.subheader("🖼️ الصورة المصغرة")
        t = st.file_uploader("", type=['jpg', 'png', 'jpeg'])
        if t: st.session_state.t_file = t

    elif st.session_state.step == 3:
        st.subheader("✍️ العنوان")
        st.session_state.v_title = st.text_input("اكتب العنوان هنا:", value=st.session_state.v_title)

    elif st.session_state.step == 4:
        st.subheader("📝 الوصف")
        st.session_state.v_desc = st.text_area("اكتب الوصف هنا:", value=st.session_state.v_desc, height=150)

    elif st.session_state.step == 5:
        st.subheader("🏷️ الكلمات")
        raw = st.text_input("أضف كلمات (فاصلة للفصل):")
        if st.button("➕ إضافة"):
            if raw:
                new = [x.strip() for x in raw.replace("،", ",").split(",") if x.strip()]
                st.session_state.tags.extend([x for x in new if x not in st.session_state.tags])
                st.rerun()
        st.multiselect("الكلمات المعتمدة:", options=st.session_state.tags, default=st.session_state.tags)

    elif st.session_state.step == 6:
        st.subheader("🕒 موعد النشر")
        # هنا تضع خيارات النشر والزر النهائي (إتمام العملية)
        st.button("📥 إرسال نهائي لليوتيوب", type="primary")

# --- 6. وحدة التحكم بالأزرار (موجودة في الأسفل دائماً على اليمين) ---
st.write("")
st.divider()

# إنشاء أعمدة: الأول للتقدم، الثاني للرجوع، الباقي فراغ
col_next, col_back, col_spacer = st.columns([3, 3, 6])

with col_next:
    if st.session_state.step < 6:
        if st.button("التقدم ➡️", key="next_universal"):
            move(st.session_state.step + 1)

with col_back:
    if st.session_state.step > 1:
        if st.button("⬅️ رجوع", key="back_universal"):
            st.session_state.step -= 1
            st.rerun()

st.caption("نظام أبو الصبري المطور 2026 ©")
