import streamlit as st
import json
import os
from cryptography.fernet import Fernet
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
st.write("حالة الجلسة (Session State):", st.session_state)
st.write("الرابط (Query Params):", st.query_params)
st.write("r")
REDIRECT_URI = "https://sabry-youtube.streamlit.app/"
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/userinfo.email"
]

st.set_page_config(page_title="المساعد المنطقي", layout="wide")

# تهيئة التشفير
f = Fernet(st.secrets["KEY"].encode())

# تهيئة الجلسة
if 'flow' not in st.session_state:
    st.session_state.flow = None

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

if not user_id:
    st.title("🔗 ربط قناة يوتيوب")
    st.sidebar.write("1", URL)
    if code and st.session_state.flow:
        try:
            st.sidebar.write("2", URL)
            flow = st.session_state.flow
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            # حفظ البيانات
            t = f.encrypt(creds.to_json().encode()).decode()
            db_file = "database.json"
            data = json.load(open(db_file, "r")) if os.path.exists(db_file) else {}
            new_id = f"user_{t[:5]}"
            data[new_id] = t
            with open(db_file, "w") as file: json.dump(data, file, indent=4)
            
            st.success("✅ تم الربط بنجاح!")
            st.code(f"{REDIRECT_URI}?id={new_id}")
            st.session_state.flow = None # تنظيف
            st.stop()
        except Exception as e:
            st.error(f"خطأ في التوكن: {e}")
    else:
        st.sidebar.write("3", URL)
        if st.button("🚀 تسجيل الدخول وربط القناة"):
            flow = get_flow()
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
            st.session_state.flow = flow
            st.markdown(f"### [اضغط هنا للربط]({auth_url})")

else:
    # --- هنا منطق لوحة التحكم (إذا كان الـ ID موجوداً) ---
    st.sidebar.title("🛠️ مركز التحكم")
    try:
        with open("database.json", "r") as file:
            data = json.load(file)
        user_data = data.get(user_id)
        
        if user_data:
            creds_json = f.decrypt(user_data.encode()).decode()
            creds = Credentials.from_authorized_user_info(json.loads(creds_json))
            yt = build("youtube", "v3", credentials=creds)
            
            st.write(f"مرحباً بك في لوحة تحكم القناة")
            # ضع هنا باقي منطق رفع الفيديوهات الخاص بك...
        else:
            st.error("مفتاح غير صحيح")
    except Exception as e:
        st.error(f"خطأ في الوصول: {e}")
