# Llama-3 Custom Persona Chatbot 🤖

A modern, sleek Streamlit chatbot application powered by **LangChain** and **Llama 3.1** (via Groq API). This chatbot allows users to choose or customize the AI's persona and specialized role before initiating the conversation, keeping a dynamically-updated chat memory tailored to the selected role.

---

## 🌟 Key Features

*   **Dynamic Persona Selection**: Select from preset roles like:
    *   **Helpful Assistant**: Friendly, helpful general chatbot.
    *   **Python Code Tutor**: Expert coding companion for writing and debugging.
    *   **Creative Writer**: Brainstorms, writes stories, and composes poetry.
    *   **Strict Critic**: Evaluates ideas with constructive skepticism.
*   **Custom Persona Configuration**: Write a tailored system prompt to define your own customized AI assistant.
*   **Interactive Sidebar Settings**: Switch roles or reset the conversation thread anytime with one click.
*   **Persistent Chat History**: Maintains chat memory throughout the session while hiding system prompts from the UI to ensure a clean chat experience.
*   **Premium Sleek Interface**: Clean dark-mode-optimized UI with custom CSS gradients and responsive badges.

---

## 🛠️ Tech Stack

*   **Frontend**: Streamlit
*   **Orchestration**: LangChain Core & LangChain Groq Integration
*   **LLM Provider**: Groq API (Running `llama-3.1-8b-instant`)
*   **Environment Manager**: python-dotenv

---

## 🚀 Getting Started

### Prerequisites
Make sure you have **Python 3.8+** installed. You will also need a **Groq API Key** which you can obtain from the [Groq Console](https://console.groq.com/).

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd MY_CHATBOT
```

### 2. Set Up a Virtual Environment
Create and activate a virtual environment to manage dependencies cleanly.

*   **Windows (PowerShell)**:
    ```powershell
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```
*   **macOS / Linux**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a file named `.env` in the root directory and add your Groq API key:
```env
GROQ_API_KEY=your_actual_groq_api_key_here
```

### 5. Run the Application
Start the Streamlit development server:
```bash
streamlit run chatbot.py
```

Once running, the application will automatically open in your default browser at `http://localhost:8501`.

---

## 📁 Project Structure

```text
MY_CHATBOT/
│
├── chatbot.py           # Main Streamlit application file
├── requirements.txt     # Python packages list
├── .env                 # Environment variables containing credentials (Ignored by Git)
├── .gitignore           # File specifying which files Git should ignore
└── README.md            # Project documentation (This file)
```

---

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).
