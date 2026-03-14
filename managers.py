import streamlit as st
import json
import os
import sys
from io import StringIO
from cryptography.fernet import Fernet
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# --- هاك الـ Print ---
if 'log_buffer' not in st.session_state:
    st.session_state.log_buffer = StringIO()
    sys.stdout = st.session_state.log_buffer

st.set_page_config(page_title="المساعد المنطقي", layout="wide")

with st.sidebar:
    st.subheader("سجل المخرجات")
    st.code(st.session_state.log_buffer.getvalue())

# --- إعدادات ثابتة ---
REDIRECT_URI = "https://sabry-youtube.streamlit.app/"
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/userinfo.email"
]

# --- منطق الربط ---
query_params = st.query_params
code = query_params.get("code")
user_id = query_params.get("id")

if not user_id:
    st.title("🔗 ربط قناة يوتيوب")
    
    # التحقق من وجود الكود في الرابط
    if code:
        # استرجاع الـ flow من ملف مؤقت أو الـ session
        # الحل الأضمن هو إعادة بناء الـ flow باستخدام نفس الإعدادات
        flow = Flow.from_client_config(
            json.loads(st.secrets["G_CRED"]),
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        try:
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            # حفظ البيانات (تأكد من وجود مفتاح KEY في secrets)
            f = Fernet(st.secrets["KEY"].encode())
            t = f.encrypt(creds.to_json().encode()).decode()
            
            # حفظ في ملف
            data = json.load(open("database.json", "r")) if os.path.exists("database.json") else {}
            new_id = f"user_{t[:5]}"
            data[new_id] = t
            with open("database.json", "w") as file: json.dump(data, file, indent=4)
            
            st.success("✅ تم الربط بنجاح!")
            st.code(f"{REDIRECT_URI}?id={new_id}")
            st.stop()
        except Exception as e:
            st.error(f"خطأ في التوكن: {e}")
            print(f"Error details: {e}")
    else:
        if st.button("🚀 تسجيل الدخول وربط القناة"):
            flow = Flow.from_client_config(
                json.loads(st.secrets["G_CRED"]),
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI
            )
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
            st.markdown(f"### [اضغط هنا للربط]({auth_url})")

else:
    st.sidebar.title("🛠️ مركز التحكم")
    # ... باقي كودك الخاص بلوحة التحكم ...
