from flask import request, redirect, flash, current_app
from helpers.helper import allowed_file, clean_markdown, get_pdf_page_count
from helpers.embedding import add_documents, generate_response, process_document
from werkzeug.utils import secure_filename
import os

class chatService:
    def healthcheck():
        return {"status": "ok"}

    def upload_file(question):
        if request.method == 'POST':
            # ตรวจสอบว่ามีไฟล์ถูกส่งมาหรือไม่
            if 'file' in request.files:
                file = request.files['file']
                # ตรวจสอบว่าไฟล์มีชื่อและเป็นรูปแบบที่ถูกต้อง
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)  # sanitize ชื่อไฟล์
                    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(save_path)  # บันทึกก่อนเรียกใช้
                    
                    total_pages = get_pdf_page_count(save_path)
                    print("📄 จำนวนหน้าทั้งหมด:", total_pages)
                    
                    all_result = []
                    for page_count in range(total_pages):
                        TASK_TYPE = "structure"
                        PAGE_NUMBER = page_count + 1
                        result = process_document(save_path, TASK_TYPE, PAGE_NUMBER)
                        cleanResult = clean_markdown(result)
                        all_result.append(cleanResult)
                    
                    combined_context = "\n".join(all_result)
                    # print("combined_context", combined_context)
                    add_documents(combined_context)
                    response = generate_response(question)
                    return response
            
            if question:
                response = generate_response(question)
                cleanResult = clean_markdown(response)
                return cleanResult
            
            return {"error": "No file or message provided"}
        
        return {"error": "Invalid request method"}
