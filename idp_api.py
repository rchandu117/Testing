from flask import Flask, request, jsonify
from idp_extraction import process_fields
import json

app = Flask(__name__)


@app.route('/idp_extraction', methods=['POST'])
def process_json():
    try:
        json_data = request.get_json() # Get the JSON data from the request
        if json_data is None:
            return jsonify({"error": "No JSON data received"}), 400

        # Assuming the JSON data has a key named 'message'
        response = process_fields(json_data)
        # Process the message or perform any other desired operations

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
