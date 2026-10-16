import json
import os
import random
import streamlit as st

st.markdown("""
<style>
.stApp { direction: rtl; text-align: right; }
[data-testid="stCode"], pre, code { direction: ltr; text-align: left; }
</style>
""", unsafe_allow_html=True)

SUBJECTS_DIR = "subjects"
ROUND_SIZE = 10


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


def open_subject(folder, name):
    st.session_state.subject = folder
    st.session_state.subject_name = name


def open_chapter(subject, folder, number, title):
    path = os.path.join(SUBJECTS_DIR, subject, folder, "questions.json")
    st.session_state.all_qs = read_json(path)
    st.session_state.chapter = folder
    st.session_state.chapter_title = f"الموضوع {number}: {title}"
    start_round()


def go_home():
    st.session_state.subject = None
    st.session_state.chapter = None


def go_chapters():
    st.session_state.chapter = None


if "subject" not in st.session_state:
    st.session_state.subject = None
if "chapter" not in st.session_state:
    st.session_state.chapter = None

st.title("بوت المراجعة")

if st.session_state.subject is None:
    st.subheader("اختر المادة")
    for folder, name in list_subjects():
        st.button(name, key=f"s_{folder}", on_click=open_subject,
                  args=(folder, name), use_container_width=True)

elif st.session_state.chapter is None:
    st.subheader(st.session_state.subject_name)
    st.button("رجوع للمواد", on_click=go_home)
    for number, title, folder in list_chapters(st.session_state.subject):
        st.button(f"الموضوع {number}: {title}", key=f"c_{folder}",
                  on_click=open_chapter,
                  args=(st.session_state.subject, folder, number, title),
                  use_container_width=True)

else:
    st.caption(f"{st.session_state.subject_name} | {st.session_state.chapter_title}")
    st.button("رجوع للمواضيع", on_click=go_chapters)

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
            if st.button("تحقق"):
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
            if st.button(label):
                st.session_state.i += 1
                st.session_state.checked = False
                st.rerun()
    else:
        answers = st.session_state.answers
        score = sum(1 for qq, a in zip(qs, answers) if a == qq["answer"])
        percent = round(score / total * 100)
        st.header(f"نتيجتك: {score} من {total} ({percent}%)")

        if percent >= 80:
            st.success("فهمك ممتاز، أنت جاهز لهذا الموضوع ✅")
        elif percent >= 50:
            st.warning("فهمك جيد، بس راجع النقاط اللي أخطأت فيها 📖")
        else:
            st.error("تحتاج ترجع تذاكر المحاضرة وتعيد المحاولة 🔁")

        st.subheader("ملخص الأسئلة")
        for n, (qq, a) in enumerate(zip(qs, answers), start=1):
            ok = a == qq["answer"]
            icon = "✅" if ok else "❌"
            st.markdown(f"**{icon} {n}. {qq['question']}**")
            if qq.get("code"):
                st.code(qq["code"], language="python")
            if not ok:
                st.write("إجابتك:", qq["options"][a])
            st.write("الإجابة الصحيحة:", qq["options"][qq["answer"]])
            st.caption(qq["explanation"])

        if st.button("جولة جديدة"):
            start_round()
            st.rerun()