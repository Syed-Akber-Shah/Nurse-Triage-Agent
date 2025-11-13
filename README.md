🚀 Setup Instructions

Step 1: Install Dependencies
pip install -r requirements.txt

Or install manually:
pip install google-genai python-dotenv

Step 2: Get Gemini API Key
Visit: https://aistudio.google.com/app/apikey
Sign in with Google account
Click "Create API Key"
Copy the key

Step 3: Create .env File
Create a file named .env in your project root:
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXX
IMPORTANT: Replace with your actual key!

Step 4: Run the Agent
python agent.py