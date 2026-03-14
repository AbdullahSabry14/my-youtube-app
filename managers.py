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
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="المساعد المنطقي", page_icon="🤖", layout="wide")

# --- 2. تهيئة الذاكرة ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.v_file = None
    st.session_state.t_file = None
    st.session_state.v_title = ""
    st.session_state.v_desc = ""
    st.session_state.tags = []
    st.session_state.show_err = False

# --- 3. تشفير ---
f = Fernet(st.secrets["KEY"].encode())
REDIRECT_URI = "https://sabry-youtube.streamlit.app/"
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/userinfo.email"
]

# --- وظائف ---
def you(c, video, pec, titel, tags, desc, pr, pu=None, prem=False):
    # (كود وظيفة النشر يبقى كما هو)
    privacy = 'private' if pu else pr
    body = {'snippet': {'title': titel, 'description': desc, 'tags': tags, 'categoryId': '22'},
            'status': {'privacyStatus': privacy, 'selfDeclaredMadeForKids': False}}
    if pu: body['status']['publishAt'] = pu.strftime('%Y-%m-%dT%H:%M:%SZ')
    med = MediaIoBaseUpload(io.BytesIO(video.read()), mimetype='video/mp4', chunksize=5 * 1024 * 1024, resumable=True)
    res = c.videos().insert(part='snippet,status', body=body, media_body=med)
    r = None
    while r is None: status, r = res.next_chunk()
    v = r['id']
    if pec:
        pec.seek(0)
        c.thumbnails().set(videoId=v, media_body=MediaIoBaseUpload(io.BytesIO(pec.read()), mimetype='image/jpeg')).execute()
    return r

# --- المنطق الأساسي ---
URL = st.query_params.get("id")
code = st.query_params.get("code")

# معالجة الربط
if not URL:
    st.title("🔗 ربط قناة يوتيوب")
    
    if code and "flow" in st.session_state:
        try:
            flow = st.session_state.flow
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            t = f.encrypt(creds.to_json().encode()).decode()
            data = json.load(open("database.json", "r")) if os.path.exists("database.json") else {}
            user_id = f"user_{t[:5]}"
            data[user_id] = t
            with open("database.json", "w") as file: json.dump(data, file, indent=4)
            
            st.success("✅ تم الربط! رابطك هو:")
            st.code(f"{REDIRECT_URI}?id={user_id}")
            st.session_state.clear()
            st.stop()
        except Exception as e:
            st.error(f"خطأ: {e}")
    else:
        if st.button("🚀 تسجيل الدخول"):
            flow = Flow.from_client_config(json.loads(st.secrets["G_CRED"]), scopes=SCOPES, redirect_uri=REDIRECT_URI)
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
            st.session_state.flow = flow
            st.markdown(f"[اضغط هنا للربط]({auth_url})")

else:
    # منطقة النشر (إذا كان ID موجود)
    # (هنا يوضع باقي كودك الخاص بالصفحات والنشر)
    st.sidebar.title("🛠️ مركز التحكم")
    # ... ضع هنا باقي كود الواجهة والـ step ...
    st.write("أنت الآن في لوحة التحكم الخاصة بـ " + URL)
