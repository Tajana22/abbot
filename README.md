# 🤖 AI Telegram Assistant + Self-Improving Repo

This project combines a Telegram AI assistant with an automated GitHub Actions AI agent that improves repository documentation.

---

## 🚀 Project Overview

This system consists of two main components:

### 1. Telegram AI Bot (Flask Webhook)
- Receives messages from Telegram users
- Processes them using OpenAI API
- Responds as a structured assistant for communication handling
- Forwards messages to admin (you)

### 2. GitHub Actions AI Agent
- Runs automatically every 2 hours
- Analyzes repository content
- Improves documentation (README, structure, comments)
- Commits and pushes updates back to repository

---

## 🧠 AI Behavior

### Telegram Bot Role
- Acts as a structured assistant for message collection
- Does NOT provide career advice or recruiting decisions
- Collects structured data:
  - Rate
  - Tech stack
  - Work format
  - Remote availability

### GitHub AI Agent Role
- Improves documentation clarity
- Enhances README structure
- Adds best practices
- Does NOT modify core application logic

---

## ⚙️ Tech Stack

- Python 3.11
- Flask
- OpenAI API
- Telegram Bot API
- GitHub Actions
- Ubuntu runner

---

## 📁 Project Structure
Certainly! Please provide the bot code so I can review it and suggest improvements inline with your instructions.
.
├── main.py # Telegram webhook bot
├── scripts/
│ └── improve_repo.py # AI GitHub Actions agent
├── README.md # Auto-improved documentation
├── requirements.txt
└── .github/workflows/
└── ai-improve.yml
---

## 🔐 Environment Variables

Create a `.env` file (for local development):


TELEGRAM_BOT_TOKEN=your_telegram_token
OPENAI_API_KEY=your_openai_key
MY_TELEGRAM_ID=your_id
PORT=5000


---

## ⚡ GitHub Actions Automation

The AI agent runs automatically:

```yaml
on:
  schedule:
    - cron: '0 */2 * * *'

This means:
👉 Every 2 hours the repository is analyzed and improved automatically.

🧠 How It Works
Telegram User → Flask Bot → OpenAI → Response → Telegram
                                   ↓
                           Forward to Admin

GitHub Actions → Python Script → OpenAI → Improve README → Commit → Push
