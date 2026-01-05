import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from controller.chatController import bp as api_v1_bp
import sys
from config import UPLOAD_FOLDER 
print("UTF-8 Mode:", sys.flags.utf8_mode)

load_dotenv()

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"Created upload folder: {UPLOAD_FOLDER}")

app = Flask(__name__)
cors = CORS(app, resources={r"/api/v1/*": {"origins": "*"}})
app.secret_key = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.register_blueprint(api_v1_bp)

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)