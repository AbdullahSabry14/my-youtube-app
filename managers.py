import streamlit as st
import json
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from cryptography.fernet import Fernet
import datetime

# --- إعدادات أساسية ---
st.set_page_config(page_title="المساعد الذكي", layout="wide")
f = Fernet("FiNtMInhiXUZNVbOud6yDJKHB6-lEjZfIq3nLPsuAmY=".encode())

# --- إعدادات OAuth ---
CLIENT_CONFIG = json.loads(st.secrets["G_CRED"]) # تأكد من وضع ملف الـ JSON في Secrets
SCOPES = ["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/userinfo.email"]
REDIRECT_URI = "https://sabry-youtube.streamlit.app/" # الرابط الخاص بك على Cloud

def get_flow():
    return Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

# --- منطق المصادقة ---
query_params = st.query_params
code = query_params.get("code")

if code:
    # المرحلة الثانية: تبادل الرمز بـ Token
    if "flow_state" in st.session_state:
        flow = get_flow()
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # حفظ الاعتمادات
        user_id = f"user_{f.encrypt(creds.to_json().encode()).decode()[:5]}"
        # (يفضل حفظ البيانات في Database خارجية أو Google Sheets لأن ملفات Cloud مؤقتة)
        st.success("تم الربط بنجاح! يمكنك الآن استخدام التطبيق.")
        st.query_params.clear()
        st.rerun()
else:
    # المرحلة الأولى: بدء المصادقة
    if st.button("🚀 تسجيل الدخول وربط القناة"):
        flow = get_flow()
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        st.session_state["flow_state"] = state
        st.markdown(f"### [اضغط هنا لتسجيل الدخول]({auth_url})")

# --- باقي الكود (وظائف الرفع you و move كما كانت) ---
# ... (ضع هنا دالة you ودالة move المعتادة)
