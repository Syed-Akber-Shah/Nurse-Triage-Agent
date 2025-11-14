# Nurse Triage Agent

## Overview
Nurse Triage Agent is an AI-powered web application designed to help healthcare staff efficiently triage patients.
The system analyzes nurses’ input to provide priority levels and recommendations, ensuring faster and more accurate hospital workflows.

## Features
- AI-based patient triage using symptoms & medical data.
- Add, update, and view patient details via secure API.
- FastAPI backend with modern REST API architecture.
- Interactive frontend (HTML/JS/CSS) for easy use.
- Ready for deployment on platforms like Deployra, Railway, Fly, or Render.
- Environment variables support for secure API keys and DB configuration.

## 🚀 Setup Instructions

Step 1 Install Dependencies:
pip install -r requirements.txt

Or install manually:
pip install google-genai python-dotenv

Step 2 Get Gemini API Key:
Visit: https://aistudio.google.com/app/apikey
Sign in with Google account
Click "Create API Key"
Copy the key

Step 3 Create .env File:
Create a file named .env in your project root:
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXX
IMPORTANT: Replace with your actual key!

Step 4 Run the Agent:
python agent.py

## Tech Stack
**Backend:**
- Python 3.11+
- FastAPI
- Uvicorn
- Pandas, NumPy
- Google Gemini AI API integration (`google-genai`)
- python-dotenv for environment variables

**Frontend:**
- HTML5 / CSS3 / JavaScript
- Responsive UI for patient management

**Deployment:**
- Deployra, Fly.io, Railway, Render compatible
- Procfile / Docker-ready structure