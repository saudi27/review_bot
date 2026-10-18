import base64
import io
import json
import os
import random
import re

import requests
import streamlit as st
from PIL import Image

try:
    from logos import LOGO_ICON_B64, LOGO_NAME_B64
except Exception:
    LOGO_ICON_B64, LOGO_NAME_B64 = "", ""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUBJECTS_DIR = os.path.join(BASE_DIR, "subjects")
ROUND_SIZE = 10

# رابط نموذج قوقل المعبأ مسبقاً (Pre-filled link) لاستقبال اقتراحات الطلاب.
# إذا تركتيه فاضي تختفي خانة الاقتراحات من الموقع.
FEEDBACK_FORM_LINK = "https://forms.gle/vtWfPoe41zVUF1Wm9"


def page_icon():
    if LOGO_ICON_B64:
        try:
            return Image.open(io.BytesIO(base64.b64decode(LOGO_ICON_B64)))
        except Exception:
            pass
    return "📘"


st.set_page_config(page_title="راجِع", page_icon=page_icon(), layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Tajawal:wght@400;500;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html { color-scheme: light; }

.stApp, .stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3,
.stApp h4, .stApp button, .stApp input, .stApp textarea {
    font-family: 'Inter', 'Tajawal', sans-serif !important;
}

/* الخلفية والاتجاه */
.stApp { background-color: #F6F5EF !important; direction: rtl; }
.block-container, [data-testid="stMainBlockContainer"] {
    padding-top: 3.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 700px !important;
}
#MainMenu, footer { visibility: hidden; }
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }

/* ألوان النصوص: كلها غامقة وواضحة */
.stApp, .stApp p, .stApp span, .stApp label, .stApp li, .stApp small,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
[data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"] {
    color: #176447 !important;
}

/* كل النصوص تبدأ من اليمين */
[data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"],
[data-testid="stAlert"], [data-testid="stRadio"] label,
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    direction: rtl !important;
    text-align: right !important;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { font-weight: 700; }

/* عنوان الصفحة: بالوسط ونازل شوي */
.page-title {
    text-align: center !important;
    direction: rtl;
    font-size: 1.6rem;
    font-weight: 700;
    color: #173B52 !important;
    margin: 1.4rem 0 1.6rem 0;
}

/* الأزرار الرئيسية: أخضر عميق ونص أبيض */
button[kind="primary"], button[data-testid="stBaseButton-primary"] {
    background-color: #A9C8B2 !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.7rem 1.4rem !important;
    box-shadow: 0 1px 3px rgba(23, 59, 82, 0.15) !important;
}
button[kind="primary"] *, button[data-testid="stBaseButton-primary"] * {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
}
button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover {
    background-color: #0F4F38 !important;
}

/* بطاقات المواد والمواضيع */
button[kind="secondary"], button[data-testid="stBaseButton-secondary"] {
    background-color: #FFFFFF !important;
    border: 1px solid #A9C8B2 !important;
    border-radius: 14px !important;
    padding: 1rem 1rem !important;
    min-height: 3.4rem;
    box-shadow: 0 1px 2px rgba(23, 59, 82, 0.08) !important;
}
button[kind="secondary"] *, button[data-testid="stBaseButton-secondary"] * {
    color: #173B52 !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    text-align: center !important;
}
button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover {
    border-color: #176447 !important;
    background-color: #F0F6F2 !important;
}

/* زر الرجوع: حواف حادة وشكل مختلف عن بطاقات المواد */
[class*="st-key-back"] button,
[class*="st-key-back"] button[kind="secondary"],
[class*="st-key-back"] button[data-testid="stBaseButton-secondary"] {
    background-color: #FFFFFF !important;
    border: 2px solid #176447 !important;
    border-radius: 4px !important;
    padding: 0.3rem 1.1rem !important;
    min-height: 0 !important;
    box-shadow: none !important;
    width: auto !important;
}
[class*="st-key-back"] button *, [class*="st-key-back"] button p {
    color: #176447 !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
}
[class*="st-key-back"] button:hover { background-color: #176447 !important; }
[class*="st-key-back"] button:hover * { color: #FFFFFF !important; }

/* زر ابدأ في صفحة البداية: متوسط وبالوسط */
[class*="st-key-start_btn"] {
    align-self: center !important;
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
}
[class*="st-key-start_btn"] [data-testid="stButton"], [class*="st-key-start_btn"] .stButton {
    display: flex !important;
    justify-content: center !important;
    width: auto !important;
}
[class*="st-key-start_btn"] button { min-width: 230px; width: auto !important; }

/* الأكواد: خلفية كحلية وكتابة من اليسار */
[data-testid="stCode"], [data-testid="stCode"] pre, pre {
    direction: ltr !important;
    text-align: left !important;
}
[data-testid="stCode"], [data-testid="stCode"] pre {
    background-color: #173B52 !important;
    border-radius: 12px !important;
}
[data-testid="stCode"] code, [data-testid="stCode"] code span {
    font-family: 'JetBrains Mono', monospace !important;
    color: #EAF1F5 !important;
    background: transparent !important;
    font-size: 0.88rem !important;
}

/* خانة الاقتراحات */
[data-testid="stTextArea"] [data-baseweb="textarea"], [data-testid="stTextArea"] [data-baseweb="base-input"] {
    background-color: #FFFFFF !important;
    border: 1px solid #A9C8B2 !important;
    border-radius: 12px !important;
}
[data-testid="stTextArea"] textarea {
    direction: rtl !important;
    text-align: right !important;
    color: #173B52 !important;
    background-color: #FFFFFF !important;
    font-size: 1rem !important;
}
[class*="st-key-feedback_btn"] button, [class*="st-key-feedback_btn"] button[kind="secondary"] {
    background-color: transparent !important;
    border: 2px dashed #A9C8B2 !important;
    box-shadow: none !important;
}

/* صفحة البداية */
.hero { text-align: center; margin-top: 4vh; direction: rtl; }
.hero img { display: inline-block; }
.hero-name-fallback { font-size: 3.4rem; font-weight: 800; color: #176447 !important; }
.welcome {
    text-align: center !important;
    color: #176447 !important;
    font-size: 1.1rem;
    font-weight: 500;
    margin: 10px 0 30px 0;
}
.mini-logo { text-align: center; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)


def logo_tag(b64, width):
    if not b64:
        return ""
    return (f'<img src="data:image/png;base64,{b64}" '
            f'style="width:{width}px; max-width:80%; height:auto;">')


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def list_subjects():
    result = []
    for folder in sorted(os.listdir(SUBJECTS_DIR)):
        info_path = os.path.join(SUBJECTS_DIR, folder, "info.json")
        if os.path.isfile(info_path):
            result.append((folder, read_json(info_path)["name"]))
    return result


def list_chapters(subject):
    result = []
    base = os.path.join(SUBJECTS_DIR, subject)
    for folder in os.listdir(base):
        info_path = os.path.join(base, folder, "info.json")
        q_path = os.path.join(base, folder, "questions.json")
        if os.path.isfile(info_path) and os.path.isfile(q_path):
            info = read_json(info_path)
            result.append((info["number"], info["title"], folder))
    return sorted(result)


def start_round():
    all_qs = st.session_state.all_qs
    n = min(ROUND_SIZE, len(all_qs))
    st.session_state.qs = random.sample(all_qs, n)
    st.session_state.i = 0
    st.session_state.answers = []
    st.session_state.checked = False
    st.session_state.rid = random.randint(0, 10**9)


def start_app():
    st.session_state.started = True


def open_subject(folder, name):
    st.session_state.subject = folder
    st.session_state.subject_name = name


def open_chapter(subject, folder, number, title):
    path = os.path.join(SUBJECTS_DIR, subject, folder, "questions.json")
    st.session_state.all_qs = read_json(path)
    st.session_state.chapter = folder
    st.session_state.chapter_title = f"الموضوع {number}: {title}"
    start_round()


def parse_form_link(link):
    m_id = re.search(r"/forms/d/e/([A-Za-z0-9_-]+)/", link or "")
    m_entry = re.search(r"entry\.(\d+)=", link or "")
    if m_id and m_entry:
        return m_id.group(1), "entry." + m_entry.group(1)
    return None, None


def send_feedback(text):
    form_id, entry = parse_form_link(FEEDBACK_FORM_LINK)    
    if not form_id:
        return False
    url = f"https://docs.google.com/forms/d/e/{form_id}/formResponse"
    try:
        r = requests.post(url, data={entry: text}, timeout=10)
        return r.status_code == 200
    except Exception:
        return False
    

def submit_feedback():
    text = (st.session_state.get("fb_text") or "").strip()
    if st.session_state.fb_count >= 5:
        st.session_state.fb_status = "limit"
    elif len(text) < 3:
        st.session_state.fb_status = "empty"
    elif send_feedback(text[:600]):
        st.session_state.fb_status = "ok"
        st.session_state.fb_count += 1
        st.session_state.fb_text = ""
    else:
        st.session_state.fb_status = "error"


def open_feedback():
    st.session_state.view = "feedback"
    st.session_state.fb_status = None


def close_feedback():
    st.session_state.view = None
    st.session_state.fb_status = None


def go_home():
    st.session_state.subject = None
    st.session_state.chapter = None


def go_chapters():
    st.session_state.chapter = None


if "started" not in st.session_state:
    st.session_state.started = False
if "subject" not in st.session_state:
    st.session_state.subject = None
if "chapter" not in st.session_state:
    st.session_state.chapter = None
if "view" not in st.session_state:
    st.session_state.view = None
if "fb_count" not in st.session_state:
    st.session_state.fb_count = 0
if "fb_status" not in st.session_state:
    st.session_state.fb_status = None

# ---------------- صفحة البداية ----------------
if not st.session_state.started:
    name_part = logo_tag(LOGO_NAME_B64, 300)
    if not name_part:
        name_part = '<div class="hero-name-fallback">راجِع</div>'
    st.markdown(
        '<div class="hero">'
        + logo_tag(LOGO_ICON_B64, 140)
        + "<br>"
        + name_part
        + '<p class="welcome">مراجعتك الذكية، لمستقبلك الأذكى</p>'
        + "</div>",
        unsafe_allow_html=True,
    )
    st.button("ابدأ", type="primary", key="start_btn", on_click=start_app)
    st.stop()

# ---------------- شعار صغير فوق باقي الصفحات ----------------
if LOGO_NAME_B64:
    st.markdown(f'<div class="mini-logo">{logo_tag(LOGO_NAME_B64, 120)}</div>',
                unsafe_allow_html=True)

# ---------------- صفحة الاقتراحات ----------------
if st.session_state.view == "feedback":
    st.button("رجوع", key="back_feedback", on_click=close_feedback)
    st.markdown('<h2 class="page-title">اقتراحاتك تهمنا</h2>', unsafe_allow_html=True)
    st.write("اكتب اقتراحك أو ملاحظتك على الموقع، أو أي شي تحب نضيفه، وراح نقرأ كل رسالة.")
    st.text_area("اقتراحك", key="fb_text", max_chars=600, height=170,
                 placeholder="اكتب هنا...", label_visibility="collapsed")
    st.button("إرسال", type="primary", key="send_fb", on_click=submit_feedback,
              use_container_width=True)
    status = st.session_state.fb_status
    if status == "ok":
        st.success("وصلت رسالتك، شكراً لك 🤍")
    elif status == "empty":
        st.warning("اكتب اقتراحك أول")
    elif status == "limit":
        st.warning("وصلت للحد الأقصى من الرسائل في هذه الجلسة")
    elif status == "error":
        st.error("تعذر إرسال الرسالة، حاول مرة ثانية بعد قليل")

# ---------------- اختيار المادة ----------------
elif st.session_state.subject is None:
    st.markdown('<h2 class="page-title">اختر المادة</h2>', unsafe_allow_html=True)
    for folder, name in list_subjects():
        st.button(name, key=f"s_{folder}", on_click=open_subject,
                  args=(folder, name), use_container_width=True)
    if parse_form_link(FEEDBACK_FORM_LINK)[0]:
        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
        st.button("💬 اقتراحات وملاحظات", key="feedback_btn", on_click=open_feedback,
                  use_container_width=True)

# ---------------- اختيار الموضوع ----------------
elif st.session_state.chapter is None:
    st.button("رجوع للمواد", key="back_subjects", on_click=go_home)
    st.markdown(f'<h2 class="page-title">{st.session_state.subject_name}</h2>',
                unsafe_allow_html=True)
    for number, title, folder in list_chapters(st.session_state.subject):
        st.button(f"الموضوع {number}: {title}", key=f"c_{folder}",
                  on_click=open_chapter,
                  args=(st.session_state.subject, folder, number, title),
                  use_container_width=True)

# ---------------- الأسئلة ----------------
else:
    st.button("رجوع للمواضيع", key="back_chapters", on_click=go_chapters)
    st.caption(f"{st.session_state.subject_name} | {st.session_state.chapter_title}")

    qs = st.session_state.qs
    i = st.session_state.i
    total = len(qs)

    if i < total:
        q = qs[i]
        st.progress(i / total)
        st.caption(f"السؤال {i + 1} من {total}")
        st.subheader(q["question"])
        if q.get("code"):
            st.code(q["code"], language="python")
        choice = st.radio(
            "اختر إجابتك:",
            q["options"],
            index=None,
            key=f"q{st.session_state.rid}_{i}",
            disabled=st.session_state.checked,
        )

        if not st.session_state.checked:
            if st.button("تحقق", type="primary", use_container_width=True):
                if choice is None:
                    st.warning("اختر إجابة أول")
                else:
                    st.session_state.answers.append(q["options"].index(choice))
                    st.session_state.checked = True
                    st.rerun()
        else:
            last = st.session_state.answers[-1]
            if last == q["answer"]:
                st.success("إجابة صحيحة ✅")
            else:
                st.error("إجابة خاطئة ❌")
                st.write("الإجابة الصحيحة:", q["options"][q["answer"]])
            st.info(q["explanation"])
            label = "السؤال التالي" if i + 1 < total else "عرض النتيجة"
            if st.button(label, type="primary", use_container_width=True):
                st.session_state.i += 1
                st.session_state.checked = False
                st.rerun()
    else:
        answers = st.session_state.answers
        score = sum(1 for qq, a in zip(qs, answers) if a == qq["answer"])
        percent = round(score / total * 100)
        st.markdown(f'<h2 class="page-title">نتيجتك: {score} من {total} ({percent}%)</h2>',
                    unsafe_allow_html=True)

        if percent >= 80:
            st.success("فهمك ممتاز، أنت جاهز لهذا الموضوع ✅")
        elif percent >= 50:
            st.warning("فهمك جيد، بس راجع النقاط اللي أخطأت فيها 📖")
        else:
            st.error("تحتاج ترجع تذاكر المحاضرة وتعيد المحاولة 🔁")

        st.button("جولة جديدة", type="primary", key="new_round", on_click=start_round,
                  use_container_width=True)
        st.button("الرجوع للصفحة الرئيسية", key="home_end", on_click=go_home,
                  use_container_width=True)

        st.subheader("ملخص الأسئلة")
        for n, (qq, a) in enumerate(zip(qs, answers), start=1):
            ok = a == qq["answer"]
            icon = "✅" if ok else "❌"
            with st.container(border=True):
                st.markdown(f"**{icon} {n}. {qq['question']}**")
                if qq.get("code"):
                    st.code(qq["code"], language="python")
                if not ok:
                    st.write("إجابتك:", qq["options"][a])
                st.write("الإجابة الصحيحة:", qq["options"][qq["answer"]])
                st.caption(qq["explanation"])

