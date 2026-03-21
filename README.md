Deploying CyberStrikeAI: Autonomous Pentesting Lab Build
Repository: backyard-labs/cyberstrikeai-lab-build
Status: Operational
Architecture: VMware Workstation (Dual-NIC Cyber Range) + External Local LLM (Ollama)

📖 Overview
This guide details the end-to-end deployment, network isolation, and operational hardening of CyberStrikeAI, an agentic AI penetration testing platform. Out of the box, the platform utilizes Chinese configurations and can suffer from "LLM vagueness" (summarizing data rather than providing raw output).

This guide covers how to:

Provision the Ubuntu VM and install the CyberStrikeAI core.

Engineer an isolated "Cyber Range" network using Netplan.

Use a Python automation script to translate the backend YAML roles to English via a local Llama 3.1 model.

Hardcode "Zero Vagueness" operational SOPs into the AI's core prompts.

📋 Prerequisites
Hypervisor: VMware Workstation Pro / Player.

OS: Ubuntu Server 22.04 LTS or 24.04 LTS ISO.

AI Engine: A host machine running Ollama with the llama3.1 model pulled and accessible over the local network.

Target: A vulnerable VM (e.g., Metasploitable2) running on an isolated VMware LAN segment (e.g., VMnet2).

🏗️ Phase 1: VM Provisioning & OS Setup
Create the Virtual Machine:

Allocate at least 4GB RAM and 2 CPU Cores.

Attach a single Network Adapter set to NAT or Bridged (we need internet access for the initial installation).

Install Ubuntu Server. Create a standard user (e.g., ali).

System Update & Dependencies:
Once booted, update the system and install required tools:

Bash
sudo apt update && sudo apt upgrade -y
sudo apt install golang-go python3 python3-pip python3-requests python3-yaml curl git -y
⚙️ Phase 2: CyberStrikeAI Installation
Fetch the Application:
(Note: Replace the URL with the official CyberStrikeAI repository/source if applicable).

Bash
cd ~
git clone https://github.com/example/CyberStrikeAI.git
cd CyberStrikeAI
Build and Verify:
Ensure the directory structure is intact, specifically the roles/ folder where the AI personas live.

Bash
go build -o cyberstrikeai main.go
# Run once to generate default configs, then stop (Ctrl+C)
./cyberstrikeai 
🛡️ Phase 3: Network Architecture (The Dual-NIC Setup)
To safely run autonomous exploits without exposing our host network, we will add a second network adapter in VMware to connect exclusively to our target range.

Hardware Configuration: In VMware settings, add a second Network Adapter and assign it to your isolated LAN segment (e.g., VMnet2).

OS Configuration (Netplan): We must configure Ubuntu to talk to the LLM on adapter 1 (ens33), and talk to the targets on adapter 2 (ens37), without creating a routing conflict.

Edit your Netplan file: sudo nano /etc/netplan/50-cloud-init.yaml

YAML
network:
  version: 2
  ethernets:
    ens33:
      dhcp4: false
      addresses:
        - 192.168.93.50/24
      routes:
        - to: default
          via: 192.168.93.2
      nameservers:
        addresses:
          - 8.8.8.8
          - 1.1.1.1
    ens37:
      dhcp4: true
      dhcp4-overrides:
        use-routes: false
Apply the configuration: sudo netplan apply

🧠 Phase 4: AI Role Hardening & Translation
By default, CyberStrikeAI stores its agent personas as Chinese YAML files. We will use a Python script and our local Llama 3.1 model to translate these and inject a strict "Zero Vagueness" reporting SOP.

Create the Automation Script:
Create a file named overhaul_roles.py in the ~/CyberStrikeAI directory:

Python
import os, yaml, requests, shutil

# Configuration
ROLES_DIR = './roles'
OUTPUT_DIR = './roles_english'
LLM_API_URL = "http://192.168.93.1:11434/api/generate" # Replace with your Ollama Host IP
MODEL_NAME = "llama3.1"

# Protect custom-built roles from being overwritten
PROTECTED_ROLES = ['Web_Sniper.yaml', 'Nmap_Scanner.yaml', '默认.yaml']

if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

def translate_content(text):
    if not text: return text
    prompt = f"""
    You are a professional security translation engine. 
    Translate the following Chinese security role content into professional English.
    If it is already in English, return it exactly as is. Maintain technical terms.
    Content: {text}
    Respond ONLY with the translated English text.
    """
    try:
        response = requests.post(LLM_API_URL, json={"model": MODEL_NAME, "prompt": prompt, "stream": False})
        return response.json().get('response', '').strip()
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return text

for filename in os.listdir(ROLES_DIR):
    if filename.endswith('.yaml'):
        src, dest = os.path.join(ROLES_DIR, filename), os.path.join(OUTPUT_DIR, filename)
        if filename in PROTECTED_ROLES:
            print(f"🛡️ Skipping: {filename}"); shutil.copy2(src, dest); continue
            
        with open(src, 'r', encoding='utf-8') as f: role_data = yaml.safe_load(f)
        print(f"🔄 Translating: {filename}...")
        
        if 'name' in role_data: role_data['name'] = translate_content(role_data['name'])
        if 'description' in role_data: role_data['description'] = translate_content(role_data['description'])
        if 'user_prompt' in role_data:
            role_data['user_prompt'] = f"{translate_content(role_data['user_prompt'])}\n\nSTRICT RULES:\n- English ONLY.\n- Output results in structured tables.\n- Never ask for permission to execute."

        with open(dest, 'w', encoding='utf-8') as f: yaml.dump(role_data, f, allow_unicode=True, sort_keys=False)

print(f"✅ Success! Saved to {OUTPUT_DIR}")
Execute the Translation:

Bash
python3 overhaul_roles.py
Deploy the Hardened Roles:

Bash
mv roles roles_backup_chinese
mv roles_english roles
🚀 Phase 5: Execution
With the network secured and the AI personas localized and hardened, start the service:

Bash
./cyberstrikeai
Access the Web UI via your browser.

Select an agent (e.g., Comprehensive Vulnerability Scanning).

Point it at a target on your isolated network (e.g., 192.168.1.108).

The agent will autonomously run tools (Nmap, Nuclei, etc.) and output strictly formatted Markdown tables.