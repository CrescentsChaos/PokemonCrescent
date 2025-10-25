import os
from flask import Flask, send_file, request, abort
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Hello. I am alive!"

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
DB_FOLDER = "./"   # change if they’re inside a subfolder

secret_key = "123"
@app.route("/download-db/<db_name>")
def download_db(db_name):
    key = "123"  # or get from request.args
    if key != secret_key:
        abort(403)

    if not db_name.endswith(".db"):
        abort(400, "Invalid file type")

    if not os.path.exists(db_name):
        abort(404, "File not found")

    return send_file(db_name, as_attachment=True)
  
if __name__ == "__main__":
    run()