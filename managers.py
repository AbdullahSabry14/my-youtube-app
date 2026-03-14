import streamlit as st
import json
import os
import sys
from io import StringIO
from cryptography.fernet import Fernet
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# إظهار المخرجات في الـ Sidebar
if 'log_buffer' not in st.session_state:
    st.session_state.log_buffer = StringIO()
    sys.stdout = st.session_state.log_buffer

st.set_page_config(page_title="المساعد المنطقي", layout="wide")

with st.sidebar:
    st.subheader("سجل المخرجات")
    st.code(st.session_state.log_buffer.getvalue())

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
    
    if code:
        # استرجاع الـ flow من ملف مؤقت لضمان بقائه
        try:
            with open("flow_state.json", "r") as f:
                flow_config = json.load(f)
            
            flow = Flow.from_client_config(
                json.loads(st.secrets["G_CRED"]),
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI
            )
            # إعادة بناء الـ flow باستخدام الـ state المخزن
            flow.fetch_token(code=code)
            
            # حفظ التوكن
            f_enc = Fernet(st.secrets["KEY"].encode())
            t = f_enc.encrypt(flow.credentials.to_json().encode()).decode()
            
            data = json.load(open("database.json", "r")) if os.path.exists("database.json") else {}
            new_id = f"user_{t[:5]}"
            data[new_id] = t
            with open("database.json", "w") as file: json.dump(data, file, indent=4)
            
            if os.path.exists("flow_state.json"): os.remove("flow_state.json")
            st.success("✅ تم الربط بنجاح!")
            st.code(f"{REDIRECT_URI}?id={new_id}")
            st.stop()
        except Exception as e:
            st.error(f"خطأ: {e}")
            print(f"Error: {e}")
    else:
        if st.button("🚀 تسجيل الدخول وربط القناة"):
            flow = Flow.from_client_config(
                json.loads(st.secrets["G_CRED"]),
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI
            )
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
            # حفظ الـ flow في ملف مؤقت
            with open("flow_state.json", "w") as f:
                json.dump({"pending": True}, f)
            st.markdown(f"### [اضغط هنا للربط]({auth_url})")

else:
    st.write("مرحباً بك في لوحة التحكم")
