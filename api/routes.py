from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
import base64
import zipfile
from io import BytesIO
import os
import sys
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.resources import get_branches, checkout_branch
from gen_ut import gen_test

# Add the parent directory of the package to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set logging level to INFO

app = Flask(__name__)
api = Api(app)
CORS(app)

# Logger instance
logger = logging.getLogger(__name__)


@app.route('/verifyRepository', methods=['POST'])
def verify():
    parser = reqparse.RequestParser()
    parser.add_argument('repo_url', type=str, required=True, help='GitHub repository URL is required')
    args = parser.parse_args()

    repo_url = args['repo_url']
    branches = get_branches(repo_url)
    return {'branches': branches}


@app.route('/selectBranch', methods=['POST'])
def checkout():
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        selected_branch = data.get('branch')
        current_path = os.getcwd()
        parent_directory = os.path.dirname(os.path.dirname(current_path))
        applicationDirectory = os.path.dirname(
            parent_directory) + "\\app"  # we will decide application name later and will configure accordingly
        logger.info(applicationDirectory)
        # Checkout branch
        checkout_branch(repo_url, selected_branch, applicationDirectory)

        return jsonify({"applicationName": "app"})
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logger.info(error_message)
        return jsonify({'error': error_message}), 500


@app.route('/generateTestCases', methods=['POST'])
def generate_test_cases():
    try:
        data = request.get_json()
        applicationname = data.get('applicationName')
        current_path = os.getcwd()
        parent_directory = os.path.dirname(os.path.dirname(current_path))
        applicationDirectory = os.path.dirname(parent_directory) + f"\\{applicationname}"

        gen_test(applicationDirectory)

        testCaseDir = os.path.dirname(parent_directory) + "\\test"

        # Create a BytesIO buffer to store the zip file in memory
        zip_buffer = BytesIO()

        # Create a zip file in memory
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(testCaseDir):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), testCaseDir))

        # Move to the beginning of the BytesIO buffer
        zip_buffer.seek(0)

        # Read the contents of the BytesIO buffer as bytes
        base64_zip = base64.b64encode(zip_buffer.read()).decode()

        # Send the zip file as bytes
        return base64_zip

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logger.info(error_message)
        return jsonify({'error': error_message}), 500


if __name__ == '__main__':
    app.run(debug=True)
