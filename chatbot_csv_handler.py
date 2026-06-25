import csv
import os
import random
import re


def load_dataset(csv_path: str):
    dataset = []
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return dataset
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'inputs' not in row or 'responses' not in row:
                continue
            inputs = [inp.strip().lower() for inp in row['inputs'].split('|') if inp.strip()]
            responses = [resp.strip() for resp in row['responses'].split('|') if resp.strip()]
            if inputs and responses:
                dataset.append({'inputs': inputs, 'responses': responses})
    return dataset


def load_short_forms(file_path: str) -> dict[str, str]:
    short_forms = {}
    if not os.path.exists(file_path):
        return short_forms

    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            shorthand = clean_text(row.get("shorthand", ""))
            full_form = clean_text(row.get("full_form", ""))
            if shorthand and full_form:
                short_forms[shorthand] = full_form
    return short_forms


def normalize_user_input(text: str, short_forms: dict[str, str] | None = None) -> str:
    cleaned = clean_text(text)
    if not short_forms:
        return cleaned

    words = cleaned.split()
    normalized_words = [short_forms.get(word, word) for word in words]
    return " ".join(normalized_words)


def clean_text(text: str) -> str:
    text = (text or "").lower().strip()
    return re.sub(r"[^\w\s]", "", text)


def load_dataset(file_path: str):
    dataset = []
    if not os.path.exists(file_path):
        return dataset

    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            inputs = [item.strip() for item in row.get("inputs", "").split("|") if item.strip()]
            responses = [item.strip() for item in row.get("responses", "").split("|") if item.strip()]
            if inputs and responses:
                dataset.append({
                    "inputs": inputs,
                    "responses": responses,
                })
    return dataset


def get_chatbot_response(user_input: str, dataset, short_forms: dict[str, str] | None = None) -> str | None:
    cleaned_input = normalize_user_input(user_input, short_forms)
    if not cleaned_input:
        return None

    for rule in dataset:
        for pattern in rule["inputs"]:
            if cleaned_input == normalize_user_input(pattern, short_forms):
                return random.choice(rule["responses"])

    for rule in dataset:
        for pattern in rule["inputs"]:
            cleaned_pattern = normalize_user_input(pattern, short_forms)
            if cleaned_pattern and re.search(r"\b" + re.escape(cleaned_pattern) + r"\b", cleaned_input):
                return random.choice(rule["responses"])

    return None
