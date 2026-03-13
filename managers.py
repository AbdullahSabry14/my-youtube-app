import streamlit as st
import datetime
import time
import requests
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
from google_auth_oauthlib.flow import InstalledAppFlow

os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="المساعد المنطقي", page_icon="🤖", layout="wide")

# --- 2. تهيئة الذاكرة (Session State) ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.v_file = None
    st.session_state.t_file = None
    st.session_state.v_title = ""
    st.session_state.v_desc = ""
    st.session_state.tags = []
    st.session_state.show_err = False 

# --- 3. جلب الـ ID من الرابط ---
URL = st.query_params.get("id")
# print(URL)
f = Fernet(st.secrets("KEY").encode())
# f = Fernet("FiNtMInhiXUZNVbOud6yDJKHB6-lEjZfIq3nLPsuAmY=".encode())
# print(f)

def send(c, t) :
    # sid = "ACe0557f10e02c653e115d0810818d2ccc"
    # tok = "c480f9562d1e76e279961bbb46c8ee49"
    # u = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    # bot = {
    #     "From" : "whatsapp:+14155238886",
    #     "To" : "whatsapp:+970595859974",
    #     "Body" : t
    # }
    # res = requests.post(u,data=bot,auth=(sid,tok))
    # return res.status_code
    # scopes = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/userinfo.email"]
    # flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes)            
    # creds = flow.run_local_server(port=0)
    ser = build("oauth2", "v2", credentials=c)
    info = ser.userinfo().get().execute()           
    my_emil = info['email']
    SENDER_EMAIL = "sbryb404@gmail.com"
    SENDER_PASSWORD = "guqb sxwk rbvr claz" # الرمز الذي ستجلبه يدوياً
    RECEIVER_EMAIL = my_emil

    msg = EmailMessage()
    msg.set_content(t)
    msg['Subject'] = 'رفع الفيديوهات على قناتك'
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)
# send("nn","ms")
def you(c, video, pec, titel, tags, desc, pr, pu=None, prem=False):
    privacy = 'private' if pu else pr
    body = {
        'snippet': {
            'title': titel,
            'description': desc,        
            'tags': tags,
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': privacy,
            'selfDeclaredMadeForKids': False
        }
    } 
    if pu :
        # iso = pu.astimezone(datetime.timezone.utc).isoformat()
        body['status']['publishAt'] = pu.strftime('%Y-%m-%dT%H:%M:%SZ')
        if prem :
            body['status']['premiere'] = True 
    med = MediaIoBaseUpload(io.BytesIO(video.read()), mimetype='video/mp4', chunksize=5 * 1024 * 1024, resumable=True)
    R = None
    error_occurred = False
    with st.spinner('...جاري إرسال البيانات إلى خادم يوتيوب'):
        try:
            res = c.videos().insert(
                part='snippet,status',
                body=body,
                media_body=med
            ) 
            r = None
            while r is None:
                status, r = res.next_chunk()
            R = r
            v = R['id']
            # if prem and v :
            #     update_body = {
            #         'id': v,
            #         'snippet': {'title': titel, 'description': desc, 'tags': tags, 'categoryId': '22'},
            #         'status': {
            #             'privacyStatus': 'public',
            #             'publishAt': pu.strftime('%Y-%m-%dT%H:%M:%SZ'),
            #             # 'premiere': True 
            #             'selfDeclaredMadeForKids': False
            #         }
            #     }
            #     c.videos().update(part='snippet,status', body=update_body).execute()
            if pec :
                pec.seek(0)
                ex = pec.name.split('.')[-1].lower()
                mime = "image/png" if ex == 'png' else "image/jpeg"
                t = MediaIoBaseUpload(io.BytesIO(pec.read()), mimetype=mime)
                c.thumbnails().set(videoId=v, media_body=t).execute()  
            return R
        except HttpError as e:
            error_occurred = True
            if e.resp.status == 400 and 'uploadLimitExceeded' in str(e):
                st.error(".⚠️ لقد وصلت للحد الأقصى لرفع الفيديوهات اليوم. يرجى المحاولة غداً")
            else:
                st.error(f"❌ حدث خطأ من يوتيوب: {e}")
        except Exception as e:
            error_occurred = True
            st.error(f"❌ حدث خطأ غير متوقع: {e}")

    if error_occurred:
        return None
    
def move(target):
    s = st.session_state
    if target > s.step:
        if s.step == 1 and not s.v_file: s.show_err = True; return
        if s.step == 2 and not s.t_file: s.show_err = True; return
        if s.step == 3 and not s.v_title.strip(): s.show_err = True; return
        if s.step == 4 and not s.v_desc.strip(): s.show_err = True; return
    s.show_err = False 
    s.step = target


if not URL :
    st.set_page_config(page_title="بوابة أبو الصبري", page_icon="🔑")

    st.markdown("<h1 style='text-align: center;'>🔗 ربط قناة يوتيوب الجديدة</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>قم بربط قناتك للحصول على رابط الرفع الخاص بك</p>", unsafe_allow_html=True)
    st.write("اضغط لتسجيل الدخول لقناتك للقدرة على التحكم ونشر فيديوهاتك :")

    if st.button("🚀 تسجيل الدخول وربط القناة الآن", use_container_width=True):
        try:
            scopes = ["https://www.googleapis.com/auth/youtube", 
                "https://www.googleapis.com/auth/youtube.upload", 
                "https://www.googleapis.com/auth/youtube.force-ssl",
                "https://www.googleapis.com/auth/userinfo.email"]
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes)            
            creds = flow.run_local_server(port=0)
            t = f.encrypt(creds.to_json().encode()).decode()
            if os.path.exists("database.json") :
                with open("database.json", "r") as file :
                    data = json.load(file)
            else :
                data = {}
            # print(creds)
            a = t[:5]
            ID = str(f"user_{a}")
            data[ID] = t
            with open("database.json", "w") as file :
                    json.dump(data, file, indent=4)
            st.success("✅ تم الربط بنجاح")
            final_link = f"https://sabry-youtube.streamlit.app/?id={ID}"
            
            st.divider()
            st.subheader("🔗 رابط الرفع الخاص بك :")
            st.code(final_link)        
        except Exception as e:
            st.error(f"❌ فشل الربط: {e}")
            st.info("تأكد من وجود ملف database.json في مجلد المشروع.")
else :
    # --- الشاشة الجانبية ---
    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>🛠️ مركز التحكم</h2>", unsafe_allow_html=True)
        st.markdown("---")
        with st.container():
            with open("database.json", "r") as file :
                data = json.load(file)
            user = data.get(URL)    
            if user :
                j = f.decrypt(user.encode()).decode()
                r = json.loads(j)
                s = Credentials.from_authorized_user_info(r)
                if s.expired :
                    s.refresh(Request())
                    new_creds_json = s.to_json()
                    encrypted_creds = f.encrypt(new_creds_json.encode()).decode()
                    with open("database.json", "r") as file :
                        data = json.load(file)
                    data[URL] = encrypted_creds
                    with open("database.json", "w") as file:
                        json.dump(data, file, indent=4)
                real = build('youtube', 'v3', credentials=s)
            else :
                st.warning("⚠️ عذراً، هذا المفتاح غير موجود في القائمة! يرجى التأكد من الرابط أو التواصل مع المسؤول.")
                st.stop()
            yt = build("youtube", "v3", credentials=s)
            channel = yt.channels().list(part="snippet", mine=True).execute()
            c_id = channel['items'][0]['id']
            st.link_button("📺 زيارة القناة", f"https://www.youtube.com/channel/{c_id}", use_container_width=True)
        st.markdown("---")
        st.markdown("### 📊 حالة الملف الحالي")
        
        # تحديث تلقائي للحالة عند اختيار الملفات
        if st.session_state.v_file: st.success(f"✅ تم اختيار: {st.session_state.v_file.name}")
        else: st.warning("⏳ بانتظار الفيديو")
        
        if st.session_state.t_file: st.success(f"✅ تم اختيار: {st.session_state.t_file.name}")
        else: st.warning("⏳ بانتظار الصورة")
        
        if st.session_state.v_title.strip() and st.session_state.v_desc.strip(): st.success("✅ البيانات النصية مكتملة")
        else: st.warning("⏳ البيانات ناقصة")
        
        st.metric(label="الكلمات المفتاحية", value=len(st.session_state.tags))
        st.markdown("---")
        if st.button("🗑️ مسح كل البيانات", use_container_width=True):
            for k in ['v_file','t_file','v_title','v_desc','tags']: 
                st.session_state[k] = None if 'file' in k else ("" if k != 'tags' else [])
            st.session_state.step = 1
            st.rerun()

    # --- 4. العناوين الثابتة ---
    st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>المساعد الذكي</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-top: 0; color: #888;'>للنشر على قناة اليوتيوب</h3>", unsafe_allow_html=True)

    st.progress((st.session_state.step - 1) / 5.0)
    st.divider()

    # --- 5. منطق الصفحات والرجوع ---
    def show_back_button():
        if st.session_state.step > 1:
            if st.button("⬅️", key=f"back_{st.session_state.step}"):
                st.session_state.step -= 1
                st.rerun()

    if st.session_state.step == 1:
        show_back_button()
        st.subheader("🎬 اختيار الفيديو")
        if st.session_state.show_err and not st.session_state.v_file: st.warning("الرجاء اختيار فيديو!")
        v_input = st.file_uploader("قم بسحب ملف الفيديو هنا", type=['mp4', 'mov'], key="v_up")
        if v_input: 
            st.session_state.v_file = v_input
            st.session_state.show_err = False

    elif st.session_state.step == 2:
        show_back_button()
        st.subheader("🖼️ اختيار الصورة المصغرة")
        if st.session_state.show_err and not st.session_state.t_file: st.warning("الرجاء اختيار صورة!")
        t_input = st.file_uploader("اختر الصورة المصغرة", type=['jpg', 'png', 'jpeg'], key="t_up")
        if t_input: 
            st.session_state.t_file = t_input
            st.session_state.show_err = False

    elif st.session_state.step == 3:
        show_back_button()
        st.subheader("✍️ عنوان الفيديو")
        if st.session_state.show_err and not st.session_state.v_title.strip(): st.warning("الرجاء كتابة العنوان!")
        st.session_state.v_title = st.text_input("العنوان:", value=st.session_state.v_title, key="title_box")

    elif st.session_state.step == 4:
        show_back_button()
        st.subheader("📝 وصف الفيديو")
        if st.session_state.show_err and not st.session_state.v_desc.strip(): st.warning("الرجاء كتابة الوصف!")
        st.session_state.v_desc = st.text_area("وصف الفيديو", value=st.session_state.v_desc, height=200, key="desc_box")
    # elif st.session_state.step == 5:
    #     show_back_button()
    #     st.subheader("🏷️ الكلمات المفتاحية")
        
    #     def add_tags_callback():
    #         raw = st.session_state.get('temp_tag_input', '')
    #         if raw:
    #             new_tags = [t.strip() for t in raw.replace("،", ",").split(",") if t.strip()]
    #             for tag in new_tags:
    #                 if tag not in st.session_state.tags:
    #                     st.session_state.tags.append(tag)
    #             st.session_state.temp_tag_input = ""

    #     st.text_input("الصق الكلمات هنا (افصل بفاصلة):", 
    #                   key="temp_tag_input", 
    #                   on_change=add_tags_callback)
        
    #     if st.button("➕ إضافة", key="btn_add_tags"):
    #         add_tags_callback()
    #         st.rerun()

    #     st.markdown("---")
        
    #     st.session_state.tags = st.multiselect(
    #         "🏷️ الكلمات المعتمدة:", 
    #         options=st.session_state.tags, 
    #         default=st.session_state.tags,
    #         key="ms_tags"
    #     )
        
    #     # --- زر التقدم لصفحة 5 (تعديل الترتيب لليمين) ---
    #     col_next_5, col_spacer_5 = st.columns([2, 10]) 
    #     with col_next_5:
    #         if st.button("التقدم ➡️", key="btn_next_step_5"):
    #             move(6)
    #             st.rerun()


    elif st.session_state.step == 5:
        show_back_button()
        st.subheader("🏷️ الكلمات المفتاحية")
        
        MAX_CHARS_LIMIT = 500 
        current_chars = sum(len(tag) for tag in st.session_state.tags)

        # 1. التنسيق الجبري (Responsive)
        st.markdown("""
            <style>
            div.tags-container {
                display: flex !important;
                flex-wrap: wrap !important;
                gap: 8px !important;
                margin-bottom: 20px !important;
            }
            
            div.stButton > button[key^="tag_btn_"] {
                background-color: #f0f7ff !important;
                color: #0056b3 !important;
                border: 1px solid #c2dbff !important;
                padding: 5px 15px !important;
                font-size: 14px !important;
                border-radius: 20px !important;
                white-space: nowrap !important;
                width: auto !important;
                display: inline-block !important;
            }
            
            div.stButton > button[key^="tag_btn_"]:hover {
                border-color: #0056b3 !important;
                background-color: #e1efff !important;
            }
            </style>
        """, unsafe_allow_html=True)

        def add_tags_callback():
            raw = st.session_state.get('temp_tag_input', '')
            if raw:
                incoming_tags = [t.strip() for t in raw.replace("،", ",").split(",") if t.strip()]
                for tag in incoming_tags:
                    tag_len = len(tag)
                    temp_total = sum(len(t) for t in st.session_state.tags)
                    if temp_total + tag_len <= MAX_CHARS_LIMIT:
                        if tag not in st.session_state.tags:
                            st.session_state.tags.append(tag)
                    else:
                        st.toast(f"⚠️ وصلت للحد الأقصى للحروف ({MAX_CHARS_LIMIT})!", icon="🛑")
                        break
                st.session_state.temp_tag_input = ""

        # 2. عرض العداد
        remaining_chars = MAX_CHARS_LIMIT - current_chars
        counter_color = "red" if remaining_chars < 20 else "#555"
        st.markdown(f'<p style="text-align: left; color: {counter_color};">عدد الحروف: <b>{current_chars}</b> / {MAX_CHARS_LIMIT}</p>', unsafe_allow_html=True)

        # 3. إدخال البيانات (تم إزالة المثال التلقائي placeholder)
        is_full = current_chars >= MAX_CHARS_LIMIT
        st.text_input(
            "أضف كلمات مفتاحية:", 
            key="temp_tag_input", 
            on_change=add_tags_callback, 
            placeholder="" if not is_full else "ممتلئ 🛑", 
            disabled=is_full
        )

        # 4. عرض الكلمات
        st.write("الكلمات المضافة:")
        tags = st.session_state.tags
        if tags:
            with st.container():
                tag_cols = st.columns(10)
                for i, tag in enumerate(tags):
                    with tag_cols[i % 10]:
                        if st.button(f"{tag} ✕", key=f"tag_btn_{i}"):
                            st.session_state.tags.remove(tag)
                            st.rerun()
        else:
            st.caption("لم يتم إضافة أي كلمات بعد.")

        st.divider()
        
        # 5. زر التقدم
        col_next_5, _ = st.columns([3, 9]) 
        with col_next_5:
            if st.button("التقدم ➡️", key="btn_next_5"):
                if current_chars > 0:
                    move(6)
                    st.rerun()
                else:
                    st.error("أضف كلمة واحدة على الأقل!")
    elif st.session_state.step == 6:
        show_back_button()
        st.subheader("🕒 إعدادات النشر النهائية")
        if 'pub_choice' not in st.session_state:
            st.session_state.pub_choice = "now"
        pub_choice = st.radio("اختر نوع النشر :", ["now", "later"], 
                              format_func=lambda x: "🚀 النشر الآن" if x == "now" else "📅 النشر لاحقاً")
        # t_now, t_later = st.tabs(["🚀 النشر الآن", "📅 النشر لاحقاً"])
        prem = False
        final_targ = None
        p_type = "public"
        
        if pub_choice == "now" :
            p_type = st.selectbox("الخصوصية:", ["public", "private", "unlisted"], 
                            format_func=lambda x: {"public": "علني", "private": "خاص", "unlisted": "غير مدرج"}[x],
                            key="p_type_now")
            st.info("سيتم النشر فوراً.")
        
        else :
            col1, col2 = st.columns(2)
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            midnight = datetime.time(0, 0)
            if 'saved_pub_date' not in st.session_state:
                st.session_state.saved_pub_date = tomorrow
                st.session_state.saved_pub_time = midnight
            # with col1:
            #     pub_date = st.date_input(": تاريخ النشر", value=st.session_state.saved_pub_date)
            # with col2:
            #     pub_time = st.time_input("وقت النشر", value=st.session_state.saved_pub_time, step=60)
            pub_date = col1.date_input("تاريخ النشر :", value=st.session_state.saved_pub_date)
            pub_time = col2.time_input("وقت النشر :", value=st.session_state.saved_pub_time, step=60)
            st.session_state.saved_pub_date = pub_date
            st.session_state.saved_pub_time = pub_time
            offset = (time.altzone if time.localtime().tm_isdst else time.timezone) / -3600
            final_targ = datetime.datetime.combine(pub_date, pub_time) - datetime.timedelta(hours=offset)
            readable_time = datetime.datetime.combine(pub_date, pub_time).strftime("%I:%M %p").replace("AM", "صباحاً").replace("PM", "مساءً")
            st.warning(f"🔔 سيتم النشر في: {pub_date} الساعة {readable_time}")
            # prem = st.checkbox("ضبط كعرض أولي")
            p_type = "public"
        st.divider()
        if st.button("📥 إتمام العملية والرفع النهائي", use_container_width=True, type="primary"):
            try :
                res = you(real, st.session_state.v_file, st.session_state.t_file, st.session_state.v_title, st.session_state.tags, st.session_state.v_desc, p_type, pu=final_targ, prem=prem)
                if res :
                    # send(s, f"✅({st.session_state.v_title}) تم رفع فيديو")
                    st.success(f"✅بنجاح ({st.session_state.v_title}) تم رفع فيديو")
                    st.balloons()
                    # time.sleep(15)
                    # for k in ['v_file','t_file','v_title','v_desc','tags']: st.session_state[k] = None if 'file' in k else ("" if k != 'tags' else [])
                    # st.session_state.step = 1
                    # st.rerun()
            except Exception as e:
                st.error(f"❌ حصل خطأ: {e}")

    # --- 6. منطقة الأزرار السفلية العامة (للمراحل 1-4) ---
    st.write("")
    # التعديل الذهبي: جعل العمود الصغير [2] هو الأول على اليمين
    col_next_gen, col_spacer_gen = st.columns([2, 10])

    with col_next_gen:
        if st.session_state.step < 5:
            if st.button("التقدم ➡️", key="global_next_btn"):
                move(st.session_state.step + 1)
                st.rerun()

st.markdown("---")
st.caption(" نظام أبو الصبري - المطور عبدالله  2026  © ")
