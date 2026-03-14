import streamlit as st
import datetime
import time
import requests
import json
import io
import os
import smtplib
from googleapiclient.errors import HttpError
from email.message import EmailMessage
from cryptography.fernet import Fernet
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow

os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="المساعد المنطقي", page_icon="🤖", layout="wide")

# --- 2. تهيئة الذاكرة (Session State) ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.v_file = None
    st.session_state.t_file = None
    st.session_state.v_title = ""
    st.session_state.v_desc = ""
    st.session_state.tags = []
    st.session_state.show_err = False 

# --- 3. الإعدادات الأساسية ---
URL = st.query_params.get("id")
f = Fernet(st.secrets["KEY"].encode())
REDIRECT_URI = "https://sabry-youtube.streamlit.app/"
SCOPES = [
    "https://www.googleapis.com/auth/youtube", 
    "https://www.googleapis.com/auth/youtube.upload", 
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/userinfo.email"
]

# --- الوظائف ---
def you(c, video, pec, titel, tags, desc, pr, pu=None, prem=False):
    privacy = 'private' if pu else pr
    body = {
        'snippet': {'title': titel, 'description': desc, 'tags': tags, 'categoryId': '22'},
        'status': {'privacyStatus': privacy, 'selfDeclaredMadeForKids': False}
    } 
    if pu:
        body['status']['publishAt'] = pu.strftime('%Y-%m-%dT%H:%M:%SZ')
        if prem: body['status']['premiere'] = True 
    
    med = MediaIoBaseUpload(io.BytesIO(video.read()), mimetype='video/mp4', chunksize=5 * 1024 * 1024, resumable=True)
    
    try:
        with st.spinner('...جاري إرسال البيانات إلى خادم يوتيوب'):
            res = c.videos().insert(part='snippet,status', body=body, media_body=med)
            r = None
            while r is None: status, r = res.next_chunk()
            v = r['id']
            if pec:
                pec.seek(0)
                mime = "image/png" if pec.name.split('.')[-1].lower() == 'png' else "image/jpeg"
                t = MediaIoBaseUpload(io.BytesIO(pec.read()), mimetype=mime)
                c.thumbnails().set(videoId=v, media_body=t).execute()
            return r
    except Exception as e:
        st.error(f"❌ حدث خطأ: {e}")
        return None

def move(target):
    s = st.session_state
    if target > s.step:
        if s.step == 1 and not s.v_file: s.show_err = True; return
        if s.step == 2 and not s.t_file: s.show_err = True; return
        if s.step == 3 and not s.v_title.strip(): s.show_err = True; return
        if s.step == 4 and not s.v_desc.strip(): s.show_err = True; return
    s.show_err = False 
    s.step = target

# --- المنطق الرئيسي ---
if not URL:
    st.markdown("<h1 style='text-align: center;'>🔗 ربط قناة يوتيوب الجديدة</h1>", unsafe_allow_html=True)
    
    code = st.query_params.get("code")
    
    if code and 'auth_flow' in st.session_state:
        try:
            flow = st.session_state.auth_flow
            flow.fetch_token(code=code)
            creds = flow.credentials
            t = f.encrypt(creds.to_json().encode()).decode()
            
            data = json.load(open("database.json", "r")) if os.path.exists("database.json") else {}
            ID = f"user_{t[:5]}"
            data[ID] = t
            json.dump(data, open("database.json", "w"), indent=4)
            
            st.success("✅ تم الربط بنجاح")
            st.code(f"{REDIRECT_URI}?id={ID}")
            del st.session_state.auth_flow
            st.stop()
        except Exception as e:
            st.error(f"❌ خطأ في التوكن: {e}")

    if st.button("🚀 تسجيل الدخول وربط القناة الآن"):
        flow = Flow.from_client_config(json.loads(st.secrets["G_CRED"]), SCOPES, redirect_uri=REDIRECT_URI)
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        st.session_state.auth_flow = flow
        st.markdown(f"### [اضغط هنا لتسجيل الدخول]({auth_url})")

else:
    # --- مركز التحكم ---
    with st.sidebar:
        data = json.load(open("database.json", "r"))
        user = data.get(URL)
        if user:
            r = json.loads(f.decrypt(user.encode()).decode())
            s = Credentials.from_authorized_user_info(r)
            if s.expired: s.refresh(Request())
            real = build('youtube', 'v3', credentials=s)
            
            channel = real.channels().list(part="snippet", mine=True).execute()
            st.link_button("📺 زيارة القناة", f"https://www.youtube.com/channel/{channel['items'][0]['id']}")
        else:
            st.warning("⚠️ مفتاح غير صالح.")
            st.stop()

    st.markdown("<h1 style='text-align: center;'>المساعد الذكي</h1>", unsafe_allow_html=True)
    st.progress((st.session_state.step - 1) / 5.0)

    # --- صفحات المعالج ---
    if st.session_state.step == 1:
        v_input = st.file_uploader("فيديو", type=['mp4', 'mov'])
        if v_input: st.session_state.v_file = v_input
    elif st.session_state.step == 2:
        t_input = st.file_uploader("صورة مصغرة", type=['jpg', 'png'])
        if t_input: st.session_state.t_file = t_input
    elif st.session_state.step == 3:
        st.session_state.v_title = st.text_input("العنوان:", value=st.session_state.v_title)
    elif st.session_state.step == 4:
        st.session_state.v_desc = st.text_area("الوصف:", value=st.session_state.v_desc)
    elif st.session_state.step == 5:
        tag_input = st.text_input("إضافة كلمات مفتاحية:")
        if tag_input: st.session_state.tags.extend(tag_input.split(','))
    elif st.session_state.step == 6:
        if st.button("📥 رفع الفيديو"):
            res = you(real, st.session_state.v_file, st.session_state.t_file, st.session_state.v_title, st.session_state.tags, st.session_state.v_desc, "public")
            if res: st.success("✅ تم الرفع!")

    if st.session_state.step < 6:
        if st.button("التقدم ➡️"): move(st.session_state.step + 1); st.rerun()

st.markdown("---")
st.caption(" نظام أبو الصبري - 2026 ©")
