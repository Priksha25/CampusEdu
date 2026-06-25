import os
import json
import urllib.parse
import urllib.request

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()
else:
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as env_file:
            for line in env_file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

GEMINI_MODEL = "gemini-3-flash-preview"
OPENAI_MODEL = "gpt-3.5-turbo"


def _extract_gemini_text(response_data: dict) -> str:
    try:
        parts = response_data["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError, TypeError):
        return ""
    return "".join(part.get("text", "") for part in parts if isinstance(part, dict)).strip()


def _ask_gemini_rest(query: str, api_key: str) -> str:
    model = urllib.parse.quote(GEMINI_MODEL, safe="")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={urllib.parse.quote(api_key)}"
    )
    payload = json.dumps({
        "contents": [
            {
                "parts": [
                    {"text": query}
                ]
            }
        ]
    }).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        response_data = json.loads(response.read().decode("utf-8"))
    return _extract_gemini_text(response_data)


def _ask_openai_rest(query: str, api_key: str) -> str:
    payload = json.dumps({
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "user", "content": query}
        ],
    }).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        response_data = json.loads(response.read().decode("utf-8"))
    try:
        return response_data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        return ""

def ask_gemini(query: str) -> str:
    """Ask Gemini through the current google-genai SDK."""
    query = (query or "").strip()
    if not query:
        return "Error contacting Gemini API: query cannot be empty"

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return "Error contacting Gemini API: GEMINI_API_KEY is not set"

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=query,
        )
        text = getattr(response, "text", "") or ""
        return text.strip() or "Error contacting Gemini API: empty response"
    except ImportError:
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(GEMINI_MODEL)
            response = model.generate_content(query)
            text = getattr(response, "text", "") or ""
            return text.strip() or "Error contacting Gemini API: empty response"
        except ImportError:
            try:
                text = _ask_gemini_rest(query, api_key)
                return text or "Error contacting Gemini API: empty response"
            except Exception as e:
                return f"Error contacting Gemini API: {e}"
        except Exception as e:
            return f"Error contacting Gemini API: {e}"
    except Exception as e:
        return f"Error contacting Gemini API: {e}"


def ask_openai(query: str) -> str:
    query = (query or "").strip()
    if not query:
        return "Error contacting OpenAI API: query cannot be empty"

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return "Error contacting OpenAI API: OPENAI_API_KEY is not set"

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": query}]
        )
        text = completion.choices[0].message.content or ""
        return text.strip() or "Error contacting OpenAI API: empty response"
    except ImportError:
        try:
            text = _ask_openai_rest(query, api_key)
            return text or "Error contacting OpenAI API: empty response"
        except Exception as e:
            return f"Error contacting OpenAI API: {e}"
    except Exception as e:
        return f"Error contacting OpenAI API: {e}"


if __name__ == "__main__":
    print(ask_gemini("linux"))
    print(ask_gemini("bash"))
