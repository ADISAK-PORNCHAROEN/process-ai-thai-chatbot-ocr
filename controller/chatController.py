from flask import Blueprint, jsonify, request
from service.chatService import chatService

# นั่นหมายความว่าทุก Route ที่เราเพิ่มเข้ามาใน 'bp' จะมี /api/v1 นำหน้าโดยอัตโนมัติ
bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

@bp.get('/healthcheck')
def healthcheck():
    try:
        checked = chatService.healthcheck()
        if checked.get("status") == "ok":
            return jsonify(checked), 200
        else:
            return jsonify({"status": "fail"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@bp.route('/chat', methods=['GET', 'POST'])
def upload_file():
    return chatService.upload_file(question=request.form.get('message'))