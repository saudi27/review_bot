import tomllib
from pypdf import PdfReader
from langchain_openai import ChatOpenAI

with open(".streamlit/secrets.toml", "rb") as f:
    key = tomllib.load(f)["OPENAI_API_KEY"]

llm = ChatOpenAI(model="gpt-4o-mini", api_key=key)

reader = PdfReader("lecture1.pdf")
kept = []

for i, page in enumerate(reader.pages, start=1):
    text = page.extract_text() or ""
    prompt = (
        "هذه صفحة من سلايدات محاضرة جامعية. "
        "إذا كانت تشرح محتوى علمي (مفاهيم، تعريفات، أمثلة، كود) اكتب: محتوى. "
        "وإذا كانت إدارية (غلاف، وصف المقرر، ساعات، فهرس، أهداف، شكرا) اكتب: اداري. "
        "اكتب كلمة واحدة فقط.\n\n" + text
    )
    verdict = llm.invoke(prompt).content.strip()
    print(i, verdict)
    if "محتوى" in verdict:
        kept.append(i)

print("صفحات المحتوى:", kept)