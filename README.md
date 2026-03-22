# 🛠️ Deploying CyberStrikeAI: Autonomous Pentesting Lab Build

**Repository:** `backyard-labs/cyberstrikeai-lab-build`
**Status:** Operational
**Architecture:** VMware Workstation (Dual-NIC Cyber Range) + External Local LLM (Ollama)

## 📖 Overview
This guide details the end-to-end deployment, network isolation, and operational hardening of **CyberStrikeAI**, an agentic AI penetration testing platform. Out of the box, the platform utilizes Chinese configurations and can suffer from "LLM vagueness" (summarizing data rather than providing raw output). 

This guide covers how to:
1. Provision the Ubuntu VM and install the CyberStrikeAI core.
2. Engineer an isolated "Cyber Range" network using Netplan.
3. Use a Python automation script to translate the backend YAML roles to English via a local Llama 3.1 model.
4. Hardcode "Zero Vagueness" operational SOPs into the AI's core prompts.

---

## 📋 Prerequisites
* **Hypervisor:** VMware Workstation Pro / Player.
* **OS:** Ubuntu Server 22.04 LTS or 24.04 LTS ISO.
* **AI Engine:** A host machine running [Ollama](https://ollama.com/) with the `llama3.1` model pulled and accessible over the local network.
* **Target:** A vulnerable VM (e.g., Metasploitable2) running on an isolated VMware LAN segment (e.g., `VMnet2`).

---

## 🏗️ Phase 1: VM Provisioning & OS Setup
1. **Create the Virtual Machine:**
   * Allocate at least **4GB RAM** and **2 CPU Cores**.
   * Attach a single Network Adapter set to **NAT** or **Bridged** (we need internet access for the initial installation).
   * Install Ubuntu Server. Create a standard user (e.g., `ali`).
2. **System Update & Dependencies:**
   Once booted, update the system and install required tools:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install golang-go python3 python3-pip python3-requests python3-yaml curl git -y
