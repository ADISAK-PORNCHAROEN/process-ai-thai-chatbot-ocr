import re
import fitz

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}
    
def clean_markdown(md_text):
    """
    ลบ Markdown syntax ที่ไม่ต้องการ เช่น ###, **bold**, ---
    """
    md_text = re.sub(r'^#+\s?', '', md_text, flags=re.MULTILINE)  # ลบ heading เช่น ###, ##
    md_text = re.sub(r'\*\*(.*?)\*\*', r'\1', md_text)            # ลบ bold **ข้อความ**
    md_text = re.sub(r'\*(.*?)\*', r'\1', md_text)                # ลบ italic *ข้อความ*
    md_text = re.sub(r'\n-{3,}\n', '\n', md_text)                 # ลบเส้นคั่น --- (3 ตัวขึ้นไป)
    return md_text.strip()
    
    
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        
def get_pdf_page_count(file_path):
    doc = fitz.open(file_path)
    page_count = doc.page_count
    doc.close()
    return page_count