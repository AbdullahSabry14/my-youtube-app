import streamlit as st
import json
import os
import sys
from io import StringIO
from cryptography.fernet import Fernet
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# --- هاك الـ Print ---
if 'log_buffer' not in st.session_state:
    st.session_state.log_buffer = StringIO()
    sys.stdout = st.session_state.log_buffer

st.set_page_config(page_title="المساعد المنطقي", layout="wide")

# عرض المخرجات في الـ Sidebar
with st.sidebar:
    st.subheader("سجل المخرجات")
    st.code(st.session_state.log_buffer.getvalue())

REDIRECT_URI = "https://sabry-youtube.streamlit.app/"
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/userinfo.email"
]

def get_flow():
    return Flow.from_client_config(
        json.loads(st.secrets["G_CRED"]),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

# --- المنطق الأساسي ---
query_params = st.query_params
code = query_params.get("code")
user_id = query_params.get("id")

if not user_id:
    st.title("🔗 ربط قناة يوتيوب")
    
    if code:
        try:
            # إعادة بناء الـ flow والتبادل مباشرة
            flow = get_flow()
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            # حفظ البيانات
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
            print(f"Exception: {e}")
    else:
        if st.button("🚀 تسجيل الدخول وربط القناة"):
            flow = get_flow()
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
            st.markdown(f"### [اضغط هنا للربط]({auth_url})")

else:
    st.write("أنت الآن في لوحة التحكم.")
