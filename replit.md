# Telegram Recruiter Bot

## Overview
A Telegram webhook bot that uses OpenAI to automatically respond to messages. The bot acts as a recruiter assistant, responding on behalf of "Tetyana" in a professional, friendly manner.

## Project Structure
- `main.py` - Main Flask application with webhook endpoint
- `test_webhook.py` - Test script for local webhook testing
- `requirements.txt` - Python dependencies

## Required Secrets
- `TELEGRAM_BOT_TOKEN` - Telegram Bot API token from @BotFather
- `OPENAI_API_KEY` - OpenAI API key for ChatGPT responses
- `MY_TELEGRAM_ID` (optional) - Your Telegram user ID to receive forwarded messages

## Endpoints
- `GET /` - Health check endpoint
- `POST /webhook` - Telegram webhook receiver

## How It Works
1. Telegram sends messages to the `/webhook` endpoint
2. The bot processes incoming text messages
3. Messages are sent to OpenAI's GPT model with a recruiter assistant prompt
4. The AI-generated response is sent back to the user
5. If configured, messages from other users are forwarded to the owner

## Running
The bot runs on port 5000 and requires the above secrets to be configured.
