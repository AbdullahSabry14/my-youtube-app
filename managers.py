import streamlit as st
import datetime
import time
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
st.set_page_config(page_title="المساعد الذكي", page_icon="🤖", layout="wide")

# --- 2. الإعدادات السرية ---
f = Fernet(st.secrets["KEY"].encode())
CLIENT_CONFIG = json.loads(st.secrets["G_CRED"])
REDIRECT_URI = "https://sabry-youtube.streamlit.app/" # تأكد أنه مطابق لما في Google Cloud

scopes = ["https://www.googleapis.com/auth/youtube", 
          "https://www.googleapis.com/auth/youtube.upload", 
          "https://www.googleapis.com/auth/userinfo.email"]

# --- 3. تهيئة الجلسة ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.v_file = None
    st.session_state.t_file = None
    # ... باقي تهيئة الحالة كما كانت

# --- وظائف الرفع (you) والارسال (send) كما هي في كودك ---
# [ضع دوال send و you هنا كما هي في كودك الأصلي]

# --- 4. منطق المصادقة ---
query_params = st.query_params
URL = query_params.get("id")
code = query_params.get("code")

if not URL:
    if code:
        flow = Flow.from_client_config(CLIENT_CONFIG, scopes=scopes, redirect_uri=REDIRECT_URI)
        flow.fetch_token(code=code)
        creds = flow.credentials
        t = f.encrypt(creds.to_json().encode()).decode()
        
        # ملاحظة: في Cloud استخدم قاعدة بيانات خارجية بدلاً من ملف JSON
        data = {} 
        ID = f"user_{t[:5]}"
        data[ID] = t
        # احفظ البيانات في مكان دائم
        st.success("✅ تم الربط! انسخ الرابط أدناه:")
        st.code(f"https://sabry-youtube.streamlit.app/?id={ID}")
        st.stop()

    st.markdown("# 🔗 ربط القناة")
    flow = Flow.from_client_config(CLIENT_CONFIG, scopes=scopes, redirect_uri=REDIRECT_URI)
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.markdown(f"### [🚀 اضغط هنا لتسجيل الدخول وربط قناتك]({auth_url})")

else:
    # --- مركز التحكم (نفس الكود السابق مع استخدام الاستعلام عن البيانات) ---
    # تأكد من تحميل بيانات المستخدم من قاعدة البيانات الخارجية
    pass
