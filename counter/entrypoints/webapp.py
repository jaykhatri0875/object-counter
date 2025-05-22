from io import BytesIO
from PIL import Image
from flask import Flask, request, jsonify
from counter import config
from counter.utils.logger_config import app_logger
import os
import uuid

# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def create_app():
    app = Flask(__name__)
    count_action = config.get_count_action()
    get_predictions_action = config.get_predictions_action()
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
            threshold = float(request.form.get('threshold', 0.5))
            uploaded_file = request.files['file']
            model_name = request.form.get('model_name', "rfcn")

            if model_name == 'rfcn':
                model_name = request.form.get('model_name', "rfcn")
                image = BytesIO()
                uploaded_file.save(image)
                count_response = count_action.execute(image, threshold)
                return jsonify(count_response)
            else:
                message = {"message": "only supporting rfcn model.", "status_code": 200}
                return jsonify(message)
        except Exception as e:
            app_logger.error(f"Error occurred while processing Request ID: {request.request_id}")
            error_message = {"error": str(e), "status_code": 400}
            return jsonify(error_message)


    @app.route('/prediction', methods=['POST'])
    def run_prediction():
        try:
            threshold = float(request.form.get('threshold', 0.5))
            uploaded_file = request.files['file']
            model_name = request.form.get('model_name', "rfcn")

            if model_name == 'rfcn':
                image = BytesIO()
                uploaded_file.save(image)
                count_response = get_predictions_action.execute(image, threshold)
                return jsonify(count_response)
            else:
                message = {"message": "only supporting rfcn model.", "status_code": 200}
                return jsonify(message)

        except Exception as e:
            app_logger.error(f"Error occurred while processing Request ID: {request.request_id}")
            error_message = {"error": str(e), "status_code": 400}
            return jsonify(error_message)

    return app

if __name__ == '__main__':
    app = create_app()
    # TODO : add ssl file for https
    app.run('0.0.0.0', debug=True)
