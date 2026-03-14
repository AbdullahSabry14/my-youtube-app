import streamlit as st
import json, io, os, smtplib, datetime, time
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from cryptography.fernet import Fernet
from email.message import EmailMessage

# إعدادات ثابتة
REDIRECT_URI = "https://sabry-youtube.streamlit.app/"
f = Fernet(st.secrets["KEY"].encode())

def get_flow():
    return Flow.from_client_config(
        client_config=json.loads(st.secrets["G_CRED"]),
        scopes=["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/userinfo.email"],
        redirect_uri=REDIRECT_URI
    )

# --- واجهة تسجيل الدخول ---
if 'creds' not in st.session_state:
    query_params = st.query_params
    if "code" not in query_params:
        flow = get_flow()
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        st.markdown(f"### [اضغط هنا لربط قناتك]({auth_url})")
        st.stop()
    else:
        flow = get_flow()
        flow.fetch_token(code=query_params["code"])
        st.session_state.creds = flow.credentials
        # تخزين الكود في قاعدة بيانات (استخدم Google Sheets أو Database خارجية في Cloud)
        # ملاحظة: في Streamlit Cloud، الملفات المؤقتة تُمسح، استخدم داتا بيز خارجية.

# --- منطق الرفع (YouTube) ---
def you(c, video, pec, title, tags, desc, privacy):
    body = {
        'snippet': {'title': title, 'description': desc, 'tags': tags, 'categoryId': '22'},
        'status': {'privacyStatus': privacy}
    }
    med = MediaIoBaseUpload(io.BytesIO(video.read()), mimetype='video/mp4', resumable=True)
    res = c.videos().insert(part='snippet,status', body=body, media_body=med).execute()
    if pec:
        c.thumbnails().set(videoId=res['id'], media_body=MediaIoBaseUpload(io.BytesIO(pec.read()), mimetype='image/jpeg')).execute()
    return res

# --- تكملة منطق واجهة المستخدم ---
# استخدم st.session_state.creds لتشغيل build('youtube', 'v3', credentials=st.session_state.creds)
