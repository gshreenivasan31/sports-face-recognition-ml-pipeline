from flask import Flask, request, jsonify, make_response
import util

app = Flask(__name__)


def build_cors_preflight_response():
    """Return a CORS preflight (OPTIONS) response."""
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response


def add_cors_headers(response):
    """Add CORS headers to normal responses."""
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/classify_image', methods=['GET', 'POST'])
def classify_image():
    image_data = request.form['image_data']
    response = jsonify(util.classify_image(image_data))
    return add_cors_headers(response)


@app.route('/describe', methods=['POST', 'OPTIONS'])
def describe():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        print("Received OPTIONS /describe (CORS preflight)")
        return build_cors_preflight_response()

    # Handle actual POST request
    data = request.get_json()
    print("Received POST /describe with JSON:", data)

    label = data.get("label") if data else None

    if not label:
        response = jsonify({"error": "Missing 'label'"})
        response.status_code = 400
        return add_cors_headers(response)

    summary = util.get_celebrity_summary(label)
    pretty_name = util._pretty_name_from_label(label)

    response = jsonify({
        "label": label,
        "name": pretty_name,
        "summary": summary
    })
    return add_cors_headers(response)


if __name__ == "__main__":
    print("Starting Python Flask Server For Sports Celebrity Image Classification")
    util.load_saved_artifacts()

    # DEBUG: print all routes so we can confirm /describe exists
    print("\n=== Registered routes ===")
    print(app.url_map)
    print("=========================\n")

    app.run(port=5000)
