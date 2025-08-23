import sys
from flask import Flask, render_template, request, session, jsonify

app = Flask(__name__)
app.secret_key = "{SECRET_KEY}"  # random generate


@app.route("/json", methods=["GET", "POST"])
def json_sample():
    data = {"sample": "json"}
    return jsonify(data), 200


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    port = 80
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    app.run(host="0.0.0.0", port=port)
