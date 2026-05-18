# AI Self-Improving Telegram Bot Repository

## Overview

This repository contains a Telegram bot application with automated AI-driven repository improvements and ephemeral CI infrastructure.

The project demonstrates:
- GitHub Actions automation
- AI-assisted repository self-improvement using LLM APIs
- Scheduled autonomous repository maintenance
- Self-hosted ephemeral GitHub runners
- Infrastructure automation for temporary VPS testing environments

---

# Features

## Telegram Bot
- Python-based Telegram bot
- Hosted on Replit
- Modular project structure
- Environment variable support for secrets

## AI Self-Improvement System
Every 2 hours, GitHub Actions automatically:
- analyzes repository documentation
- improves README structure and clarity
- updates developer-oriented documentation
- applies safe repository improvements
- commits changes back to GitHub automatically

## Ephemeral CI Infrastructure
The repository also includes infrastructure automation for:
- temporary Hetzner VPS creation
- self-hosted GitHub Actions runner setup
- isolated test execution
- automatic VPS destruction after tests
- cost-efficient CI/CD workflows

---

# Repository Structure

```text
.
├── .github/workflows/      # GitHub Actions workflows
├── infra/                  # Infrastructure automation scripts
├── scripts/                # AI automation scripts
├── main.py                 # Telegram bot application
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── tests/                  # Automated tests
```

---

# Technologies Used

- Python 3.11
- GitHub Actions
- OpenAI API
- Replit
- Hetzner Cloud
- Linux
- Git
- CI/CD automation

---

# AI Automation Workflow

The workflow runs automatically every 2 hours using GitHub Actions cron scheduling.

Main automation steps:
1. Checkout repository
2. Install dependencies
3. Run AI improvement script
4. Generate documentation improvements
5. Commit and push updates automatically

Workflow file:
```text
.github/workflows/ai-self-improve.yml
```

---

# Setup

## Clone Repository

```bash
git clone https://github.com/your-username/your-repository.git
cd your-repository
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment Variables

Create environment variables:

```bash
OPENAI_API_KEY=your_api_key
BOT_TOKEN=your_telegram_token
```

---

# Running Locally

```bash
python main.py
```

---

# GitHub Secrets

The following repository secrets are required:

| Secret Name | Description |
|---|---|
| OPENAI_API_KEY | OpenAI API key |
| BOT_TOKEN | Telegram bot token |
| HETZNER_TOKEN | Hetzner Cloud API token |

---

# CI/CD Infrastructure

The project includes:
- scheduled AI repository improvements
- automated testing
- ephemeral VPS deployment
- self-hosted GitHub runners
- temporary infrastructure lifecycle management

Infrastructure is automatically destroyed after test execution to minimize cloud costs.

---

# Security Notes

- Secrets are stored using GitHub Secrets
- No hardcoded credentials
- No public SSH exposure for VPS runners
- Tunnel-based secure remote access

---

# Future Improvements

- Extended automated documentation generation
- Static analysis integration
- Automated linting improvements
- Expanded test coverage
- Infrastructure monitoring

---

# Author

DevOps / Automation / AI Infrastructure Test Assignment

```
