# 🛡️ Shadow Swarm: The Adversarial Security Guard

<img src="https://raw.githubusercontent.com/umang-algo/Shadow-Swarm/master/assets/hero.png" width="800" alt="Shadow Swarm Hero">

> **The defensive shield of the DevAgent Ecosystem.**  
> *Shadow Swarm "attacks" your code to find vulnerabilities, logic leaks, and insecure patterns, ensuring your autonomous software is also unhackable.*

Shadow Swarm is a specialized adversarial agent that performs Deep-Tissue security scans of your repositories. It combines static analysis (Bandit/Safety) with AI-driven security reviews to identify risks that traditional linters miss.

---

## 🌟 Key Features

- **🛡️ Red-Team Scanning**: Recursive static analysis of codebases to find insecure imports, logic flaws, and untrusted data handling.
- **👁️ AI Adversary**: Uses Claude to perform "hacker-mindset" code reviews, identifying architectural leaks and hardcoded secrets.
- **🔌 Oracle Integration**: Feeds security vulnerabilities directly to **Oracle** as high-priority fix tasks for **Ghost**.
- **📊 Vulnerability Board**: A clear, severity-ranked view of the current security posture of your projects.

---

## 🛠️ Quick Start

### 1. Setup
```bash
git clone https://github.com/umang-algo/Shadow-Swarm.git
cd Shadow-Swarm
pip install -r requirements.txt
cp .env.example .env
```

### 2. Scan for Vulnerabilities
Perform a security audit of the current directory:
```bash
python3 shadow.py
```

---

## 🛡️ License
MIT License
