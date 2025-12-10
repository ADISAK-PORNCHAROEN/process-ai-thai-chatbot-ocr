from sentence_transformers import SentenceTransformer
from db import getConnection
from openai import OpenAI
import os
from dotenv import load_dotenv
from typhoon_ocr import prepare_ocr_messages
import json
import time

load_dotenv()

conn = getConnection()
cur = conn.cursor()

embedder = SentenceTransformer("BAAI/bge-m3")

client = OpenAI(
    base_url=os.getenv("TYPHOON_BASE_URL"),
    api_key=os.getenv("TYPHOON_API_KEY")
)

def add_documents(documents):
    embeddings = embedder.encode(documents).tolist()
    cur.execute("INSERT INTO documents (content, embedding) VALUES (%s, %s)", (documents, embeddings))
    conn.commit()

def query_documents(query, k=5):
    query_embedding = embedder.encode(query).tolist()
    
    query_embedding_str = "[" + ", ".join(map(str, query_embedding)) + "]"
    
    sql_query = """
        SELECT content, embedding <=> %s::vector AS similarity_score
        FROM documents
        ORDER BY similarity_score ASC
        LIMIT %s;
    """
    
    cur.execute(sql_query, (query_embedding_str, k))
    results = cur.fetchall()
    return results

def generate_response(query_text):
    start = time.time()

    retrievend_docs = query_documents(query_text, 5)
    
    context = "\n".join([doc[0] for doc in retrievend_docs])
    prompt = f"""
    ต่อไปนี้คือบริบทที่อาจเกี่ยวข้องกับคำถามของผู้ใช้และอ้างอิงจากข้อมูลในฐานข้อมูล โปรดสรุปข้อความต่อไปนี้ให้กระชับ หากไม่มีข้อมูลเพียงพอ โปรดตอบจากความรู้ของคุณ:
    {context}

    คำถาม: {query_text}
    """
    
    response = client.chat.completions.create(
        model=os.getenv("TYPHOON_MODEL"),
        messages=[
            {"role": "system", "content": "คุณชื่อ Typhoon เป็นผู้ช่วยที่เป็นมิตรและให้ข้อมูลที่เป็นประโยชน์แก่ผู้ใช้ คุณจะตอบคำถามเป็นภาษาไทยที่สุภาพและเข้าใจง่าย"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=512,
        temperature=0.6,
        top_p=0.95,
    )

    end = time.time()
    print(f"Time taken: {end - start:.2f} seconds")

    return response.choices[0].message.content

# print(response.choices[0].message.content)
# print(generate_response("ได้รับหน้าที่ให้ทำอะไร"))

def process_document(pdf_or_image_path, task_type="default", page_number=1):
    """
    ประมวลผลเอกสาร PDF หรือรูปภาพด้วย Typhoon OCR
    
    Args:
        pdf_or_image_path (str): path ของไฟล์ PDF หรือรูปภาพ
        task_type (str): "default" หรือ "structure"
        page_number (int): หมายเลขหน้าสำหรับ PDF (default: 1)
    
    Returns:
        str: ข้อความที่ได้จาก OCR
    """
    
    # ตรวจสอบว่าไฟล์มีอยู่หรือไม่
    if not os.path.exists(pdf_or_image_path):
        return f"❌ ไม่พบไฟล์: {pdf_or_image_path}"
    
    try:
        print(f"🔄 กำลังประมวลผล: {pdf_or_image_path}")
        print(f"📄 หน้าที่: {page_number}")
        print(f"🎯 โหมด: {task_type}")
        print("-" * 50)
        
        # เตรียม OCR messages
        messages = prepare_ocr_messages(
            pdf_or_image_path=pdf_or_image_path,
            task_type=task_type,
            target_image_dim=1800,
            target_text_length=8000,
            page_num=page_number
        )
        
        print("✅ เตรียมข้อมูลสำเร็จ กำลังส่งไปยัง API...")
        
        # ส่งไปยัง Typhoon OCR API
        response = client.chat.completions.create(
            model=os.getenv("TYPHOON_OCR_MODEL"),
            messages=messages,
            max_tokens=16384,
            extra_body={
                "repetition_penalty": 1.2,
                "temperature": 0.1,
                "top_p": 0.6,
            },
        )
        
        text_output = response.choices[0].message.content
        
        # พยายามแปลง JSON และดึง natural_text
        try:
            json_data = json.loads(text_output)
            markdown_result = json_data.get('natural_text', "").replace("<figure>", "").replace("</figure>", "")
        except Exception as e:
            print(f"⚠️ ไม่สามารถแปลง JSON ได้: {str(e)}")
            print("📝 ใช้ output ดิบแทน...")
            markdown_result = text_output
        
        return markdown_result
    
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาด: {str(e)}"