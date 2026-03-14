# Final Project: Biodiversity Agent Chatbot

## Setup and Running

1. **Set your API Key**
   Add your API key to `backend/.env`:
   ```env
   GEMINI_API_KEY=your_key_here
   ```

2. **Run the Backend**
   ```bash
   cd final_project/backend
   source venv/bin/activate
   pip install -r requirements.txt # or install dynamically
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

3. **Run the Frontend**
   ```bash
   cd final_project/frontend
   npm install
   npm run dev
   ```

Open `http://localhost:5173` to interact with the Biodiversity Sentinel Agent!
