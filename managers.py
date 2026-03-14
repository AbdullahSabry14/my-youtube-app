import streamlit as st
import datetime
import time
import json
import io
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from cryptography.fernet import Fernet

# --- إعدادات ---
st.set_page_config(page_title="المساعد المنطقي", page_icon="🤖", layout="wide")
f = Fernet("FiNtMInhiXUZNVbOud6yDJKHB6-lEjZfIq3nLPsuAmY=".encode())
SCOPES = ["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/userinfo.email"]
REDIRECT_URI = "https://sabry-youtube.streamlit.app/" # رابط تطبيقك في السحاب

# --- تهيئة الـ Flow ---
def get_flow():
    return Flow.from_client_config(
        json.loads(st.secrets["G_CRED"]),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

# --- منطق الربط ---
query_params = st.query_params
code = query_params.get("code")
user_id = query_params.get("id")

if code and not user_id:
    # مرحلة تبادل الكود بالـ Token
    flow = get_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials
    
    # حفظ الكريدنشلز في ملف أو قاعدة بيانات
    t = f.encrypt(creds.to_json().encode()).decode()
    data = {}
    if os.path.exists("database.json"):
        with open("database.json", "r") as file: data = json.load(file)
    
    new_id = f"user_{t[:5]}"
    data[new_id] = t
    with open("database.json", "w") as file: json.dump(data, file)
    
    st.success("✅ تم الربط! الرابط الخاص بك:")
    st.code(f"{REDIRECT_URI}?id={new_id}")
    st.stop()

elif not user_id:
    # شاشة تسجيل الدخول
    st.title("🔗 ربط قناة يوتيوب")
    flow = get_flow()
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    st.markdown(f"### [اضغط هنا لتسجيل الدخول لقناتك]({auth_url})")
    st.stop()

else:
    # مرحلة التحكم بعد الربط
    with open("database.json", "r") as file: data = json.load(file)
    user_data = data.get(user_id)
    
    if not user_data:
        st.error("مفتاح غير صحيح")
        st.stop()

    creds_json = json.loads(f.decrypt(user_data.encode()).decode())
    creds = Credentials.from_authorized_user_info(creds_json)
    
    if creds.expired:
        creds.refresh(Request())
        # تحديث الكود المشفر في الملف...
        
    yt = build("youtube", "v3", credentials=creds)
    # باقي منطق الرفع الخاص بك هنا...
    st.success("مرحباً بك في لوحة التحكم")
