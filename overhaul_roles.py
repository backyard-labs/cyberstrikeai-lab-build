import os
import yaml
import requests
import shutil

# Configuration
ROLES_DIR = './roles'
OUTPUT_DIR = './roles_english'
LLM_API_URL = "http://192.168.93.1:11434/api/generate"
MODEL_NAME = "llama3.1"

# PROTECT THESE FILES - Exact matches from your filesystem
PROTECTED_ROLES = ['Web_Sniper.yaml', 'Nmap_Scanner.yaml', '默认.yaml']

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def translate_content(text):
    if not text:
        return text

    prompt = f"""
    You are a professional security translation engine.
    Translate the following Chinese security role content into professional English.
    If it is already in English, return it exactly as is.
    Maintain the technical meaning and use 'Zero Vagueness' terminology.

    Content: {text}

    Respond ONLY with the translated English text. No explanations.
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(LLM_API_URL, json=payload)
        return response.json().get('response', '').strip()
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return text

# Loop through all YAML files
for filename in os.listdir(ROLES_DIR):
    if filename.endswith('.yaml') or filename.endswith('.yml'):
        source_path = os.path.join(ROLES_DIR, filename)
        dest_path = os.path.join(OUTPUT_DIR, filename)

        # --- THE PROTECTION CHECK ---
        if filename in PROTECTED_ROLES:
            print(f"🛡️ Skipping Protected Role: {filename}")
            shutil.copy2(source_path, dest_path)
            continue

        with open(source_path, 'r', encoding='utf-8') as f:
            role_data = yaml.safe_load(f)

        print(f"🔄 Translating: {filename}...")

        # Translate key fields
        if 'name' in role_data:
            role_data['name'] = translate_content(role_data['name'])
        if 'description' in role_data:
            role_data['description'] = translate_content(role_data['description'])
        if 'user_prompt' in role_data:
            translated_prompt = translate_content(role_data['user_prompt'])
            # Inject our operational SOP rules into every translated role
            role_data['user_prompt'] = f"{translated_prompt}\n\nSTRICT RULES:\n- English ONLY.\n- Output results in structured tables.\n- Never ask for permission to execute."

        # Save the new version
        with open(dest_path, 'w', encoding='utf-8') as f:
            yaml.dump(role_data, f, allow_unicode=True, sort_keys=False)

print(f"✅ Success! All roles processed and saved to {OUTPUT_DIR}")