import json
import os
import random
import tomllib
from pypdf import PdfReader
from langchain_openai import ChatOpenAI

folder = input("Chapter folder (example: subjects/trf301/chapter1): ").strip()

with open(".streamlit/secrets.toml", "rb") as f:
    key = tomllib.load(f)["OPENAI_API_KEY"]

llm = ChatOpenAI(model="gpt-4o-mini", api_key=key, temperature=0.2)

reader = PdfReader(os.path.join(folder, "lecture.pdf"))
pages = {}
text = ""
for i, page in enumerate(reader.pages, start=1):
    page_text = page.extract_text() or ""
    pages[i] = page_text
    text += f"\n--- صفحة {i} ---\n" + page_text
    
prompt = (
    "أنت مساعد مراجعة لطلاب مبتدئين. هذا نص سلايدات محاضرة، وكل صفحة مرقمة. "
    "ملاحظة: بعض الكلمات العربية في النص قد تظهر معكوسة الحروف بسبب استخراج الـ PDF، فافهمها بتمعن.\n\n"
    "القواعد:\n"
    "1. اكتب الأسئلة من السلايدات فقط. ممنوع أي معلومة من خارج المحاضرة.\n"
    "2. الجواب الصحيح لازم يكون عبارة موجودة في السلايد، بنفس صياغتها أو قريبة جداً منها، "
    "بحيث الطالب يلقاها بسهولة لما يرجع للسلايد. اكتب السؤال بنفس مصطلحات السلايد.\n"
    "3. الأسئلة مباشرة وواضحة للمبتدئين: بدون تلاعب، بدون استنتاج، بدون تفكير عميق. "
    "لا تكتب سؤال عام مثل 'ما هو تعريف كذا' إلا لو السلايد يعرّفه صراحة بجملة.\n"
    "4. الخيارات الخاطئة تكون معلومات من سلايدات أخرى في نفس المحاضرة (مثل خاصية نموذج ثاني) "
    "أو عكس المعلومة الصحيحة. ممنوع الخيارات الغريبة أو المضحكة أو من خارج المحاضرة، "
    "وممنوع تكون كل الخيارات متشابهة مع كلمة واحدة مختلفة.\n"
    "5. خيار واحد فقط صحيح بوضوح.\n"
    "6. اكتب سؤال أو سؤالين لكل سلايد فيه محتوى علمي، بدون تكرار الفكرة، حتى 40 سؤال.\n"
    "7. تجاهل الأغلفة، وصف المقرر، الساعات، قائمة الموضوعات، التقييم، الأهداف، "
    "تعليمات فتح Colab، تفاصيل الكود، وصفحة الشكر.\n\n"
    "مثال سيء: 'ما هو تعريف RNN؟' بخيارات عن أنواع التعلم (التعلم المعزز، غير المراقب...) "
    "لأن السلايدات ما تتكلم عنها.\n"
    "مثال جيد: 'كيف تعالج RNN الكلمات؟' الصحيح: 'كلمة واحدة في كل خطوة بشكل تسلسلي'، "
    "والخاطئ: 'جميع الكلمات دفعة واحدة' (لأنها خاصية Transformer).\n"
    "مثال سيء: 'ما هو مفهوم Vanishing Gradient؟' بخيارات عامة.\n"
    "مثال جيد: 'ما اسم المشكلة اللي تضعف فيها المعلومات مع زيادة طول التسلسل في RNN؟' "
    "الصحيح: 'مشكلة تلاشي التدرج (Vanishing Gradient)'.\n\n"
    "أرجع النتيجة بصيغة JSON فقط بدون أي كلام قبلها أو بعدها، على شكل قائمة، "
    "وكل عنصر فيه المفاتيح: question, options (قائمة من 4 نصوص), "
    "answer (رقم الخيار الصحيح من 0 إلى 3), explanation (جملة قصيرة من السلايد), "
    "page (رقم الصفحة كرقم فقط).\n\n"
    + text
)

reply = llm.invoke(prompt).content
reply = reply.replace("```json", "").replace("```", "").strip()
candidates = json.loads(reply)

seen_pages = set()
seen_questions = set()
unique = []
for q in candidates:
    k1 = (q["page"], q["options"][q["answer"]])
    k2 = q["question"].strip()
    if k1 not in seen_pages and k2 not in seen_questions:
        seen_pages.add(k1)
        seen_questions.add(k2)
        unique.append(q)

kept = []
for q in unique:
    try:
        slide_text = pages[int(q["page"])]
    except (KeyError, ValueError, TypeError):
        continue
    correct = q["options"][q["answer"]]
    options_text = "\n".join("- " + o for o in q["options"])
    check = (
        "هذا نص سلايد واحد من محاضرة (قد تكون بعض الكلمات العربية معكوسة الحروف):\n"
        + slide_text
        + "\n\nالسؤال: " + q["question"]
        + "\nالخيارات:\n" + options_text
        + "\nالإجابة المقترحة: " + correct
        + "\n\nافحص الشروط الثلاثة:\n"
        "1. الإجابة المقترحة مكتوبة صراحة في نص هذا السلايد.\n"
        "2. باقي الخيارات خاطئة بوضوح حسب المحاضرة، ولا يوجد خيار ثاني صحيح.\n"
        "3. السؤال واضح ومباشر ومناسب لمبتدئ ولا يحتاج استنتاج.\n"
        "اكتب: نعم إذا تحققت الشروط الثلاثة، وإلا اكتب: لا. كلمة واحدة فقط."
    )
    verdict = llm.invoke(check).content.strip()
    if verdict.startswith("نعم"):
        kept.append(q)

for q in kept:
    correct = q["options"][q["answer"]]
    random.shuffle(q["options"])
    q["answer"] = q["options"].index(correct)

with open(os.path.join(folder, "questions.json"), "w", encoding="utf-8") as f:json.dump(kept, f, ensure_ascii=False, indent=2)

print("المقترح:", len(candidates), "| بعد حذف المكرر:", len(unique), "| بعد المراجعة:", len(kept))