from flask import Flask, send_from_directory,request,jsonify,send_file,render_template
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)  # Abilita CORS per tutto l'app Flask

# Configura la directory per i file statici (i tuoi log della chat)
CHAT_LOG_DIR = "chat_logs"
app.config["CHAT_LOG_DIR"] = CHAT_LOG_DIR

@app.route('/')
def index():
    print("Gestione della richiesta per index.html")  # Aggiungi questo print per debug
    return render_template('index.html')

@app.route("/join")
def join():
    cod_film = request.args.get("cod_film")
    return jsonify({"status": "success", "message": f"Joined film {cod_film}"})

@app.route("/request_metasource")
def request_metasource():
    cod_film = request.args.get("cod_film")
    metasource_filename = f'metasource{cod_film}.txt'
    if os.path.exists(metasource_filename):
        with open(metasource_filename, 'r') as metasource_file:
            metasource_content = metasource_file.read()

        print(f"Metasource received: {metasource_content}")
        return jsonify({"status": "success", "data": metasource_content})
    else:
        return jsonify({"status": "error", "message": f"Metasource not found for cod_film: {cod_film}"})

@app.route("/download")
def download_file():
    file = request.args.get("file")
    print(file)
    path = f"chat_log{file}.txt"
    print(path)
    try:
        return send_file(path, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "File not found"})

@app.route("/get_chat_log")
def get_chat_log():
    cod_film = request.args.get("cod_film")
    filename = f"chat_log{cod_film}.txt"
    try:
        with open(filename, 'r') as file:
            chat_log_content = file.read()
        return jsonify({"status": "success", "content": chat_log_content})
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "Chat log not found"})

# Avvia l'app Flask
if __name__ == "__main__":
    # Assicurarsi che la directory dei log della chat esista
    if not os.path.exists(CHAT_LOG_DIR):
        os.makedirs(CHAT_LOG_DIR)

    app.run(port=5000)
