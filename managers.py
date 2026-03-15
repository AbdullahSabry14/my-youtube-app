
import streamlit as st
import datetime
import time
import requests
import json
import io
import os
import smtplib
import socket
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

# إعدادات العميل (تم وضع بياناتك هنا)
CLIENT_CONFIG = {
    "web": {
        "client_id": "952304570944-3fc213vjepobs71m8uru1jph4aguaiu0.apps.googleusercontent.com",
        "project_id": "mymy-469310",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["https://sabry-youtube.streamlit.app/"]
    }
}

REDIRECT_URI = "https://sabry-youtube.streamlit.app/"
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/userinfo.email"
]

if 'step' not in st.session_state:
    st.session_state.update({'step': 1, 'v_file': None, 't_file': None, 'v_title': "", 'v_desc': "", 'tags': [], 'show_err': False})

URL = st.query_params.get("id")
f = Fernet("FiNtMInhiXUZNVbOud6yDJKHB6-lEjZfIq3nLPsuAmY=".encode())

def you(c, video, pec, titel, tags, desc, pr, pu=None, prem=False):
    privacy = 'private' if pu else pr
    body = {'snippet': {'title': titel, 'description': desc, 'tags': tags, 'categoryId': '22'},
            'status': {'privacyStatus': privacy, 'selfDeclaredMadeForKids': False}}
    if pu:
        body['status']['publishAt'] = pu.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    med = MediaIoBaseUpload(io.BytesIO(video.read()), mimetype='video/mp4', chunksize=5 * 1024 * 1024, resumable=True)
    try:
        res = c.videos().insert(part='snippet,status', body=body, media_body=med).execute()
        v = res['id']
        if pec:
            pec.seek(0)
            t = MediaIoBaseUpload(io.BytesIO(pec.read()), mimetype="image/jpeg")
            c.thumbnails().set(videoId=v, media_body=t).execute()
        return res
    except Exception as e:
        st.error(f"❌ حدث خطأ: {e}")
        return None

# --- منطق الربط ---
if not URL:
    st.markdown("<h1 style='text-align: center;'>🔗 ربط قناة يوتيوب</h1>", unsafe_allow_html=True)
    code = st.query_params.get("code")
    
    if not code:
        flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES, redirect_uri=REDIRECT_URI)
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        st.link_button("🚀 تسجيل الدخول وربط القناة", auth_url, use_container_width=True)
    else:
        flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES, redirect_uri=REDIRECT_URI)
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        t = f.encrypt(creds.to_json().encode()).decode()
        data = json.load(open("database.json", "r")) if os.path.exists("database.json") else {}
        ID = f"user_{t[:5]}"
        data[ID] = t
        with open("database.json", "w") as file: json.dump(data, file, indent=4)
        st.success(f"تم الربط! الرابط الخاص بك هو: `http://localhost:8501/?id={ID}`")
else:
    # (هنا تكمل باقي كود الواجهة والتحكم الخاص بك كما كان)
    st.write("تم الدخول بنجاح")
