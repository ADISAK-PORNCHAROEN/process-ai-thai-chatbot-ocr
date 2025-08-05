import time
from flask import request, redirect, flash, current_app
from helpers.helper import allowed_file, clean_markdown, get_pdf_page_count
from helpers.embedding import add_documents, generate_response, process_document
from werkzeug.utils import secure_filename
import os
from multiprocessing.dummy import Pool as ThreadPool

class chatService:
    def healthcheck():
        return {"status": "ok"}


    def upload_file(question):
        if request.method == 'POST':
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename != '' and allowed_file(file.filename):
                    start = time.time()
                    filename = secure_filename(file.filename)
                    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(save_path)
                    
                    total_pages = get_pdf_page_count(save_path)
                    print("📄 จำนวนหน้าทั้งหมด:", total_pages)
                    
                    def process_page_wrapper(page_count):
                        try:
                            TASK_TYPE = "structure" 
                            PAGE_NUMBER = page_count + 1
                            result = process_document(save_path, TASK_TYPE, PAGE_NUMBER)
                            cleanResult = clean_markdown(result)
                            print(f"✅ เสร็จแล้วหน้า {page_count + 1}")
                            return cleanResult
                        except Exception as e:
                            print(f"❌ Error หน้า {page_count + 1}: {e}")
                            return ""
                    
                    # ใช้ thread pool
                    pool_size = min(3, total_pages)
                    with ThreadPool(pool_size) as pool:
                        all_result = pool.map(process_page_wrapper, range(total_pages))
                    
                    combined_context = "\n".join(filter(None, all_result))
                    add_documents(combined_context)
                    response = generate_response(question)
                    cleanResult = clean_markdown(response)
                    end = time.time()
                    print(f"Time taken: {end - start:.2f} seconds")
                    return cleanResult
                    
            if question:
                start = time.time()
                response = generate_response(question)
                cleanResult = clean_markdown(response)
                end = time.time()
                print(f"Time taken: {end - start:.2f} seconds")
                return cleanResult
            return {"error": "No file or message provided"}
        return {"error": "Invalid request method"}
