# 🎓 CampusEdu Smart Chatbot v2.0

CampusEdu is a highly interactive, intelligent chatbot framework that seamlessly integrates local database rules, dynamic dataset lookup, document Q&A (PDF & DOCX), and LLM fallback engines (OpenAI & Gemini). It supports both a command-line interface (CLI) with rich text layouts and a web-based dashboard interface.

---

## 🚀 Features

- **Multi-Source Response Pipeline**:
  1. **Local Database Check**: Instant matching against highly customized triggers.
  2. **CSV Dataset Match**: Fuzzy matching and abbreviation resolution based on local datasets.
  3. **Document Q&A**: Scan, parse, and answer questions directly from PDF or Word (`.docx`) files.
  4. **LLM Fallback (OpenAI/Gemini)**: Intelligent responses when local sources do not have the answer.
- **Dual Interface Modes**:
  - **Console (CLI)**: Beautiful terminal user interface built using the `rich` library with spin loaders, status headers, and panels.
  - **Web Dashboard**: An interactive, responsive browser chat application served locally.
- **Automatic Environment Verification**: A helper startup script ensures all dependencies are present and up to date before launching.
- **Docker Containerization**:
  - Build once and run anywhere using Docker.
  - Simplified deployment and dependency management.
  - Supports both CLI and Web Dashboard execution.

---

## 👥 Contributors

| Name | Contribution |
|------|-------------|
| Anurag | Frontend Development, API Integration, Deployment |
| Priksha Nehra | Backend Development, Research, Data Collection |
| Gurjeet Singh | Testing, Docker Configuration and Containerization |

---

## 📥 Clone the Repository

```bash
git clone https://github.com/<your-username>/CampusEdu.git
cd CampusEdu
```

---

## 🛠️ Prerequisites

1. **Python**: Python 3.8 or higher installed and added to your system's `PATH`.
2. **API Keys (Optional but Recommended)**:
   - **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/)
   - **OpenAI API Key** from [OpenAI Platform](https://platform.openai.com/)

---

## ⚙️ Project Setup & Configuration

### 1. Configure Environment Variables
Create a file named `.env` in the root directory (if it does not already exist) and populate it with your API keys:

```env
# Gemini API Key (Get it from https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI API Key (Get it from https://platform.openai.com/)
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Prepare Data Files
Ensure that the `data/` directory contains your database rules:
- `data/chatbot_dataset.csv`: The main query-response dataset.
- `data/short_qa.csv`: A dictionary of short abbreviations or quick QA maps.

---

## 🏃 Running the Chatbot

### Option A: Quick Start (Windows)
Double-click or run **`CampusEdu.bat`** (or **`CampasEdu.bat`**) from your terminal:
```cmd
CampusEdu.bat
```
*This script will:*
1. Verify if Python is installed.
2. Run `check_requirements.py` to inspect installed modules.
3. Automatically install missing packages listed in `requirement.txt`.
4. Create the `data/` directory if missing.
5. Launch the **CLI Chatbot** (`main.py`).

---

### Option B: Manual Startup (Any OS)

1. **Install Dependencies**:
   ```bash
   pip install -r requirement.txt
   ```

2. **Run the CLI Chatbot**:
   ```bash
   python main.py
   ```

3. **Run the Web Interface Chatbot**:
   ```bash
   python web.py
   ```
   Open your browser and navigate to: **`http://127.0.0.1:8000`**

---

## 🐳 Docker Support

CampusEdu can be deployed and executed inside a Docker container, ensuring a consistent environment across different systems.

### Build the Docker Image

```bash
docker build -t campusedu .
```

### Run the Container

```bash
docker run -it --env-file .env campusedu
```

### Run with Port Mapping (Web Interface)

```bash
docker run -it -p 8000:8000 --env-file .env campusedu
```

Then open:

```text
http://localhost:8000
```

### Docker Benefits

* Consistent environment across Windows, Linux, and macOS
* Simplified deployment process
* Dependency isolation
* Easy scalability and distribution
* Faster onboarding for new contributors

### Verify Docker Installation

```bash
docker --version
docker compose version
```

If Docker is installed correctly, both commands should display version information.`

---

## 💬 Chatbot Commands (CLI Mode)

When chatting in the CLI, you can use these special commands to control the session:

| Command | Description |
|:---|:---|
| `/doc <filename>` | Load a PDF or DOCX file for local context Q&A. |
| `<filename>.pdf` | Auto-detect and load the specified PDF document directly. |
| `<filename>.docx` | Auto-detect and load the specified Word document directly. |
| `/clear` | Unload the active document and exit document Q&A mode. |
| `/help` | Show the commands reference table. |
| `exit` / `quit` / `bye` | Close the CLI chatbot session safely. |

---

## 📂 Project Structure

```plaintext
├── .env                     # API key configurations
├── requirements.txt          # Python dependencies
├── CampusEdu.bat            # One-click Windows startup script
├── Dockerfile               # Docker container configuration
├── .dockerignore            # Docker ignore rules
├── check_requirements.py    # Requirement checking utility
├── main.py                  # CLI Orchestration pipeline (Main entrypoint)
├── web.py                   # Web server entrypoint
├── API_Fallback.py          # Fallback logic for LLM processing
├── db_Config.py             # Database initializations and rule matching
├── chatbot_csv_handler.py   # Helper methods for loading datasets & short-forms
├── document_qa.py           # Parsing and questioning of PDFs & DOCX files
├── networkDiagnostics.py    # Connectivity diagnostic utilities
├── data/                    # Local storage directory for dataset files
└── web_static/              # Frontend files for the Web Chatbot UI (HTML, CSS, JS)
```

---

## 🧰 Technology Stack

- Python
- HTML, CSS, JavaScript
- OpenAI API
- Google Gemini API
- Docker
- Rich (CLI UI)
- CSV Dataset Processing
- PDF & DOCX Parsing
