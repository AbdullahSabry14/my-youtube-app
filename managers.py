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

# --- الإعدادات ---
st.set_page_config(page_title="المساعد المنطقي", page_icon="🤖", layout="wide")
f = Fernet("FiNtMInhiXUZNVbOud6yDJKHB6-lEjZfIq3nLPsuAmY=".encode())
SCOPES = ["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/userinfo.email"]
REDIRECT_URI = "https://sabry-youtube.streamlit.app/" # تأكد من مطابقة هذا الرابط لما وضعته في Google Cloud

# --- تهيئة الذاكرة ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.v_file = None
    st.session_state.t_file = None
    st.session_state.v_title = ""
    st.session_state.v_desc = ""
    st.session_state.tags = []

# --- وظيفة بناء الـ Flow ---
def get_flow():
    return Flow.from_client_config(
        json.loads(st.secrets["G_CRED"]),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

# --- منطق الربط وتسجيل الدخول ---
query_params = st.query_params
code = query_params.get("code")
URL = query_params.get("id")

if not URL and not code:
    st.markdown("<h1 style='text-align: center;'>🔗 ربط قناة يوتيوب</h1>", unsafe_allow_html=True)
    flow = get_flow()
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
    st.markdown(f"### [اضغط هنا لتسجيل الدخول لقناتك]({auth_url})")

elif code and not URL:
    flow = get_flow()
    try:
        flow.fetch_token(code=code)
        creds = flow.credentials
        t = f.encrypt(creds.to_json().encode()).decode()
        
        # ملاحظة: في Cloud استخدم قاعدة بيانات خارجية مثل Google Sheets أو Firestore 
        # لأن نظام الملفات المحلي يمسح البيانات عند إعادة التشغيل
        ID = f"user_{t[:5]}"
        st.success("✅ تم الربط! هذا هو رابط قناتك الخاص:")
        st.code(f"https://sabry-youtube.streamlit.app/?id={ID}")
        st.info("قم بحفظ هذا الرابط في مكان آمن.")
    except Exception as e:
        st.error(f"خطأ في الربط: {e}")

else:
    # هنا تضع كود التشغيل (المركز الجانبي والخطوات 1-6)
    # تأكد من استدعاء البيانات من مصدر دائم وليس database.json محلي
    st.sidebar.title("🛠️ مركز التحكم")
    st.write("أنت الآن داخل لوحة التحكم الخاصة بك.")
    # ... (باقي كود خطوات الرفع هنا)
