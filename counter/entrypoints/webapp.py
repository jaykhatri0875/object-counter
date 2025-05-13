from io import BytesIO

from flask import Flask, request, jsonify

from counter import config

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def create_app():
    
    app = Flask(__name__)
    
    count_action = config.get_count_action()
    
    @app.route('/object-count', methods=['POST'])
    def object_detection():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        threshold = float(request.form.get('threshold', 0.5))
        uploaded_file = request.files['file']

        if uploaded_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if uploaded_file and allowed_file(uploaded_file.filename):
            model_name = request.form.get('model_name', "rfcn")
            image = BytesIO()
            uploaded_file.save(image)
            count_response = count_action.execute(image, threshold) # TODO : add model name as argument to be passed in ml service
            return jsonify(count_response)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run('0.0.0.0', debug=True)
