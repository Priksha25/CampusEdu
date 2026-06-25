import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from API_Fallback import ask_gemini
from chatbot_csv_handler import get_chatbot_response, load_dataset, load_short_forms
from db_Config import init_database, query_local_db
from networkDiagnostics import is_online


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "web_static")
DATA_DIR = os.path.join(BASE_DIR, "data")
DATASET = load_dataset(os.path.join(DATA_DIR, "chatbot_dataset.csv"))
SHORT_FORMS = load_short_forms(os.path.join(DATA_DIR, "short_qa.csv"))


def build_response(user_input: str) -> tuple[str, str]:
    db_answer = query_local_db(user_input)
    if db_answer:
        return db_answer, "Database"

    dataset_answer = get_chatbot_response(user_input, DATASET, SHORT_FORMS)
    if dataset_answer:
        return dataset_answer, "Dataset"

    if not is_online():
        return "Network connection is unavailable. Gemini cannot be reached right now.", "System"

    return ask_gemini(user_input), "Gemini"


class ChatbotWebHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/chat":
            self.send_json({"error": "Not found"}, status=404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body or "{}")
            message = str(payload.get("message", "")).strip()
        except (ValueError, json.JSONDecodeError):
            self.send_json({"error": "Invalid JSON body"}, status=400)
            return

        if not message:
            self.send_json({"error": "Message cannot be empty"}, status=400)
            return

        answer, source = build_response(message)
        self.send_json({
            "answer": answer,
            "source": source,
        })

    def send_json(self, payload: dict, status: int = 200):
        response = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)


def run(host: str = "127.0.0.1", port: int = 8000):
    init_database()
    server = ThreadingHTTPServer((host, port), ChatbotWebHandler)
    print(f"CampusEdu web chatbot running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    run()
