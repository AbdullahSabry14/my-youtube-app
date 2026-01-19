import streamlit as st
import datetime
import time
import requests
import pickle
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

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


def send(t) :
    sid = "ACe0557f10e02c653e115d0810818d2ccc"
    tok = "c480f9562d1e76e279961bbb46c8ee49"
    u = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    bot = {
        "From" : "whatsapp:+14155238886",
        "To" : "whatsapp:+970595859974",
        "Body" : t
    }
    res = requests.post(u,data=bot,auth=(sid,tok))
    return res.status_code

def get() :
    with open ("token.pickle", "rb") as t :
        o = pickle.load(t) 
    return build("youtube", "v3", credentials=o)

def you(video, pec, titel, tags, desc, pr, pu=None) :
    i = get()
    body = {
            'snippet': {
                'title': titel,
                'description': desc,
                'tags': tags,
                'categoryId': '22'
            },
            'status': {
                'privacyStatus': pr,
                'selfDeclaredMadeForKids': False
            }
        }
    if pu :
        of = time.strftime("%z")
        if not of : of = "+02:00"
        iso = pu.strftime(f'%Y-%m-%dT%H:%M:%S{of}')
        body['status']['privacyStatus'] = 'private'
        body['status']['publishAt'] = iso
    med = MediaIoBaseUpload(io.BytesIO(video.read()), mimetype='application/octet-stream', chunksize=-1, resumable=True)
    res = i.videos().insert(
        part='snippet,status',
        body=body,
        media_body=med
    )
    R = None
    while R is None :
        شش, R = res.next_chunk()
    if R and pec :
        v = R['id']
        pec.seek(0) 
        ex = pec.name.split('.')[-1].lower()
        if ex == 'jpg': mime = "image/jpeg"
        elif ex == 'png': mime = "image/png"
        else: mime = "image/jpeg"
        t = MediaIoBaseUpload(io.BytesIO(pec.read()), mimetype=mime)
        try:
            i.thumbnails().set(videoId=v, media_body=t).execute()
        except Exception as thumb_err:
            st.warning(f"⚠️ تم رفع الفيديو ولكن فشل رفع الصورة المصغرة: {thumb_err}")
    return R

    
def move(target):
    s = st.session_state
    if target > s.step:
        if s.step == 1 and not s.v_file: s.show_err = True; return
        if s.step == 2 and not s.t_file: s.show_err = True; return
        if s.step == 3 and not s.v_title.strip(): s.show_err = True; return
        if s.step == 4 and not s.v_desc.strip(): s.show_err = True; return
    s.show_err = False 
    s.step = target


# --- 3. الشاشة الجانبية (خليتها زي ما هي) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🛠️ مركز التحكم</h2>", unsafe_allow_html=True)
    st.markdown("---")
    with st.container():
        st.link_button("📺 زيارة القناة", "https://www.youtube.com/channel/UCUYZPlOw92cDnQ4wmlsLnNg", use_container_width=True)
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
st.markdown("<p style='text-align: center;'>معكم في كل زمان ومكان</p>", unsafe_allow_html=True)

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

elif st.session_state.step == 5:
    show_back_button()
    st.subheader("🏷️ الكلمات المفتاحية")
    
    # 1. التنسيق الجبري - إجبار الـ 6 أعمدة في التلفون
    st.markdown("""
        <style>
        /* أهم سطر: يمنع ستريمليت من قلب الأعمدة تحت بعض في الموبايل */
        [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important; /* يمنع النزول لسطر جديد داخل الصف الواحد */
            gap: 2px !important; /* تقليل المسافة جداً لتكفي الشاشة */
        }
        
        [data-testid="column"] {
            width: 16% !important; /* تقريباً سدس العرض */
            min-width: unset !important;
            flex: 1 1 0% !important;
        }

        /* تنسيق الأزرار (شفاف وبدون مسافات) */
        div.stButton > button {
            background-color: transparent !important;
            color: #24292e !important;
            border: 1px solid #d1d5da !important;
            padding: 2px 2px !important; /* تقليل الحواف الداخلية للحد الأدنى */
            border-radius: 5px !important;
            font-size: 10px !important; /* تصغير الخط قليلاً ليناسب شاشة الجوال */
            width: 100% !important;
            white-space: nowrap !important;
            overflow: hidden;
            text-overflow: clip; /* قص النص الزائد */
        }
        
        div.stButton > button:hover {
            border-color: #0366d6 !important;
            color: #0366d6 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    def add_tags_callback():
        raw = st.session_state.get('temp_tag_input', '')
        if raw:
            new_tags = [t.strip() for t in raw.replace("،", ",").split(",") if t.strip()]
            for tag in new_tags:
                if tag not in st.session_state.tags:
                    st.session_state.tags.append(tag)
            st.session_state.temp_tag_input = ""

    # 2. إدخال البيانات
    st.text_input("اكتب واضغط Enter:", key="temp_tag_input", on_change=add_tags_callback)

    # 3. عرض الكلمات (6 كلمات في كل سطر غصب عن التلفون)
    st.write("الكلمات:")
    
    tags = st.session_state.tags
    if tags:
        for i in range(0, len(tags), 6):
            row_tags = tags[i:i+6]
            cols = st.columns(6) 
            for j, tag in enumerate(row_tags):
                with cols[j]:
                    # حذف الكلمة عند الضغط
                    if st.button(f"{tag}✕", key=f"tag_btn_{i+j}"):
                        st.session_state.tags.remove(tag)
                        st.rerun()
    else:
        st.caption("لا توجد كلمات حالياً.")

    st.divider()
    
    # 4. زر التقدم
    col_next_5, _ = st.columns([3, 9]) 
    with col_next_5:
        if st.button("التقدم ➡️", key="btn_next_5"):
            move(6)
            st.rerun()
elif st.session_state.step == 6:
    show_back_button()
    st.subheader("🕒 إعدادات النشر النهائية")
    t_now, t_later = st.tabs(["🚀 النشر الآن", "📅 النشر لاحقاً"])
    targ = None
    p_type = "public"
    
    with t_now:
        p_type = st.radio("الخصوصية:", ["public", "private", "unlisted"], 
                         format_func=lambda x: {"public": "علني", "private": "خاص", "unlisted": "غير مدرج"}[x],
                         key="p_type_now")
        st.info("سيتم الرفع ومعالجة البيانات فوراً.")
    
    with t_later:
        col1, col2 = st.columns(2)
        with col1:
            pub_date = st.date_input(": تاريخ النشر", value=datetime.date.today())
        with col2:
            suggested_time = (datetime.datetime.now() + datetime.timedelta(minutes=10)).time()
            pub_time = st.time_input(": وقت النشر", value=suggested_time, key="t_input")
        st.checkbox("ضبط كعرض أول فوري")
        targ = datetime.datetime.combine(pub_date, pub_time)
        
    st.divider()
    if st.button("📥 إتمام العملية والرفع النهائي", use_container_width=True, type="primary"):
        # منطق الرفع (نفسه الموجود عندك)
        with st.spinner('...جاري إرسال البيانات إلى خادم يوتيوب'):
            try :
                res = you(st.session_state.v_file, st.session_state.t_file, st.session_state.v_title, st.session_state.tags, st.session_state.v_desc, p_type, pu=targ)
                if res :
                    st.success(f"✅ تم رفع فيديو ({st.session_state.v_title}) بنجاح")
                    send(f"✅ تم رفع فيديو ({st.session_state.v_title})")
                    st.balloons()
                    time.sleep(2)
                    for k in ['v_file','t_file','v_title','v_desc','tags']: st.session_state[k] = None if 'file' in k else ("" if k != 'tags' else [])
                    st.session_state.step = 1
                    st.rerun()
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
