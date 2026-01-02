from flask import Flask
import time

app = Flask(__name__)

@app.route("/")
def index():
    start = time.time()
    # Simula 50 ms di CPU
    while time.time() - start < 0.05:
        pass
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
