from io import BytesIO
from PIL import Image
from flask import Flask, request, jsonify
from counter import config
from counter.utils.logger_config import app_logger
import os
import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def create_app():
    app = Flask(__name__)
    count_action = config.get_count_action()
    @app.before_request
    def before_request():
        request.request_id = str(uuid.uuid4())
        app_logger.info(f"Request ID: {request.request_id} - Incoming request: {request.method} {request.path}")

    @app.after_request
    def after_request(response):
        app_logger.info(f"Request ID: {request.request_id} - Request completed with status code: {response.status_code}")
        response.headers['X-Request-ID'] = request.request_id
        return response

    @app.route('/object-count', methods=['POST'])
    def object_detection():
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400

            threshold = float(request.form.get('threshold', 0.5)) # default value is 0.5
            uploaded_file = request.files['file']


            if uploaded_file.filename == '':
                app_logger.error('blank name received')
                return jsonify({'error': 'No selected file'}), 400

            if uploaded_file and allowed_file(uploaded_file.filename):
                model_name = request.form.get('model_name', "rfcn") # not used in current implementation
                uploaded_file_name = str(request.request_id) + str(uploaded_file.filename)
                upload_file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file_name)
                uploaded_file.save(upload_file_path) # inorder to save file to any given location

                uploaded_file_img_bytes = uploaded_file.read()

                if model_name == 'rfcn':
                    count_response = count_action.execute(uploaded_file_img_bytes, threshold)
                    # deleting the file after usage if required to do so
                    # os.remove(os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file_name))
                    # TODO: check respone before sending back
                    return jsonify(count_response)
                else:
                    # TODO : add other models
                    message = {"message": "only supporting rfcn model.", "status_code": 200}
                    return jsonify(message)
            else:
                message = {"message": "uploaded file is not allowed. please use 'png', 'jpg', 'jpeg' formats only.", "status_code": 200}
                return jsonify(message)

        except Exception as e:
            app_logger.error(f"Error occurred while processing Request ID: {request.request_id}")
            error_message = {"error": str(e), "status_code": 400}
            return jsonify(error_message)

    @app.route('/prediction', methods=['POST'])
    def run_prediction():
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400
            threshold = float(request.form.get('threshold', 0.5)) # default value is 0.5
            uploaded_file = request.files['file']

            if uploaded_file.filename == '':
                app_logger.error('blank name received')
                return jsonify({'error': 'No selected file'}), 400

        except Exception as e:
            app_logger.error(f"Error occurred while processing Request ID: {request.request_id}")
            error_message = {"error": str(e), "status_code": 400}
            return jsonify(error_message)

    return app

if __name__ == '__main__':
    app = create_app()
    # TODO : add ssl file for https
    app.run('0.0.0.0', debug=True)
