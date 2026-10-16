from pypdf import PdfReader

reader = PdfReader("lecture1.pdf")

for i, page in enumerate(reader.pages[:12], start=1):
    page_text = page.extract_text() or ""
    print(i, "|", len(page_text), "|", page_text[:60].replace("\n", " "))