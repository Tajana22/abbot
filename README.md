# AI Self-Improving Telegram Bot Repository

## Overview

This repository contains a Python-based Telegram bot integrated with an automated AI-driven repository self-improvement system and ephemeral CI infrastructure.

### Key Highlights

- Automated GitHub Actions workflows for repository maintenance  
- AI-assisted documentation and code improvements using large language model (LLM) APIs  
- Scheduled autonomous repository updates every 2 hours  
- Self-hosted ephemeral GitHub runners on temporary VPS instances  
- Infrastructure automation for cost-efficient, isolated testing environments  

---

## Features

### Telegram Bot

- Python 3.11 Telegram bot built with the Flask framework  
- Modular and maintainable project structure  
- Hosted on Replit for easy deployment  
- Supports environment variables for secure secret management  

### AI Self-Improvement System

- Runs every 2 hours via GitHub Actions cron schedule  
- Analyzes and improves repository documentation and developer guides  
- Applies safe, incremental repository improvements  
- Automatically commits and pushes changes back to GitHub  

### Ephemeral CI Infrastructure

- Automates creation and teardown of temporary Hetzner VPS instances  
- Sets up self-hosted GitHub Actions runners on VPS  
- Runs isolated tests in ephemeral environments  
- Automatically destroys infrastructure post-testing to reduce costs  

---

## Repository Structure

```
.
├── .github/workflows/      # GitHub Actions workflow definitions  
├── infra/                  # Infrastructure automation scripts (e.g., VPS setup)  
├── scripts/                # AI automation and improvement scripts  
├── tests/                  # Automated test suites  
├── main.py                 # Telegram bot application entrypoint  
├── requirements.txt        # Python dependencies  
└── README.md               # Project documentation  
```

---

## Technologies Used

- Python 3.11  
- Flask web framework  
- GitHub Actions for CI/CD automation  
- OpenAI API for AI-driven improvements  
- Replit hosting platform  
- Hetzner Cloud for ephemeral VPS infrastructure  
- Linux environment  
- Git version control  

---

## AI Automation Workflow

The AI self-improvement workflow runs every 2 hours using GitHub Actions cron syntax.

### Workflow Steps

1. Checkout repository code  
2. Install Python dependencies  
3. Execute AI improvement scripts to analyze and update documentation and code  
4. Commit and push any safe improvements automatically  

Workflow configuration file:  
`.github/workflows/ai-self-improve.yml`

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repository.git
cd your-repository
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root or export environment variables in your shell with the following keys:

```bash
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
MY_TELEGRAM_ID=your_telegram_user_id  # Optional, for personalized features
```

> **Note:** Ensure these environment variables are set before running the bot.

---

## Running the Bot Locally

Start the Telegram bot with:

```bash
python main.py
```

The bot will listen for incoming messages and respond using AI-generated replies.

---

## GitHub Repository Secrets

To enable full CI/CD and infrastructure automation, configure the following repository secrets in your GitHub repository settings:

| Secret Name    | Description                          |
| -------------- | ---------------------------------- |
| OPENAI_API_KEY | OpenAI API key for AI services     |
| BOT_TOKEN      | Telegram bot token                  |
| HETZNER_TOKEN  | Hetzner Cloud API token for VPS management |

---

## CI/CD and Infrastructure Details

- Scheduled AI repository improvements via GitHub Actions  
- Automated test execution with ephemeral infrastructure  
- Temporary VPS deployment on Hetzner Cloud for isolated runners  
- Self-hosted GitHub Actions runners configured dynamically  
- Infrastructure lifecycle management ensures automatic teardown post-tests to minimize costs  

---

## Security Considerations

- All sensitive credentials are managed securely via GitHub Secrets and environment variables  
- No hardcoded secrets or tokens in the codebase  
- VPS runners do not expose public SSH access; secure tunnel-based remote access is used  
- Logs and error handling implemented to avoid leaking sensitive information  

---

## Future Enhancements

Planned improvements include:

- Extended automated documentation generation  
- Integration of static code analysis tools  
- Automated linting and code style enforcement  
- Expanded test coverage for robustness  
- Infrastructure monitoring and alerting capabilities  

---

## Author

DevOps / Automation / AI Infrastructure Test Assignment

---

## Application Code Overview and Commenting Suggestions

- **Logging:** Configured at INFO level with timestamps for effective debugging and monitoring.  
- **Environment Variables:** Loaded via `dotenv` with safe checks to avoid crashes if missing.  
- **OpenAI Client:** Lazily initialized only if API key is present to prevent runtime errors.  
- **Flask App:** Simple web server to handle Telegram webhook or polling requests.  
- **Chat History:** Maintains up to 10 recent messages per chat to provide context for AI responses.  
- **System Prompt:** Defined in Ukrainian to personalize the assistant's behavior.  
- **Response Cleaner:** Removes common greetings from AI responses to keep replies concise and relevant.  
- **Telegram Message Sender:** Handles message sending with error logging and token presence checks.  
- **ChatGPT Interaction:** Wraps OpenAI API calls with error handling and maintains conversation state.  
- **Routes:** Minimal GET route for health check returning "OK".  

### Suggested Code Comment Improvements

- Add comprehensive docstrings to all functions describing parameters, return values, and purpose.  
- Document the structure and expected format of `chat_history` for maintainability.  
- Clarify the rationale behind limiting chat history length to 10 messages to balance context and performance.  
- Explain the choice of the `gpt-4o-mini` model and fallback behavior if unavailable.  
- Include comments on security practices, e.g., why environment variables are preferred over hardcoding secrets.  
- Add inline comments in complex blocks like `clean_response` to explain the greeting removal logic and regex usage.  
- Consider adding consistent type hints for all functions and variables to improve readability and maintainability.