import streamlit as st
import json
import os
import sys
from io import StringIO
from cryptography.fernet import Fernet
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# --- إعدادات المخرجات في الـ Sidebar ---
if 'log_buffer' not in st.session_state:
    st.session_state.log_buffer = StringIO()
    sys.stdout = st.session_state.log_buffer

st.set_page_config(page_title="المساعد المنطقي", layout="wide")

with st.sidebar:
    st.subheader("سجل المخرجات")
    st.code(st.session_state.log_buffer.getvalue())

# --- الثوابت ---
REDIRECT_URI = "https://sabry-youtube.streamlit.app/"
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/userinfo.email"
]

# --- المنطق ---
query_params = st.query_params
code = query_params.get("code")
user_id = query_params.get("id")

def get_base_flow():
    return Flow.from_client_config(
        json.loads(st.secrets["G_CRED"]),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

if not user_id:
    st.title("🔗 ربط قناة يوتيوب")
    
    if code:
        try:
            flow = get_base_flow()
            # تبادل الكود بالتوكن مباشرة
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            # التشفير والحفظ
            f_enc = Fernet(st.secrets["KEY"].encode())
            t = f_enc.encrypt(creds.to_json().encode()).decode()
            
            db_file = "database.json"
            data = json.load(open(db_file, "r")) if os.path.exists(db_file) else {}
            new_id = f"user_{t[:5]}"
            data[new_id] = t
            with open(db_file, "w") as file: json.dump(data, file, indent=4)
            
            st.success("✅ تم الربط بنجاح!")
            st.code(f"{REDIRECT_URI}?id={new_id}")
            st.stop()
        except Exception as e:
            st.error(f"خطأ في التوكن: {e}")
            print(f"Exception details: {e}")
    else:
        if st.button("🚀 تسجيل الدخول وربط القناة"):
            flow = get_base_flow()
            # استخدام access_type='offline' للحصول على refresh_token دائم
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
            st.markdown(f"### [اضغط هنا للربط]({auth_url})")

else:
    # --- لوحة التحكم ---
    st.sidebar.title("🛠️ مركز التحكم")
    try:
        if os.path.exists("database.json"):
            with open("database.json", "r") as file:
                data = json.load(file)
            user_data = data.get(user_id)
            if user_data:
                st.write("✅ القناة مرتبطة وجاهزة.")
            else:
                st.error("مفتاح غير صحيح")
    except Exception as e:
        st.error(f"خطأ في الوصول: {e}")
