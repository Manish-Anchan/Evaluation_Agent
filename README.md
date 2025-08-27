# 🤖 Evaluation Agent

An **AI-powered evaluation assistant** built with **Streamlit**, **LangGraph**, and **LangChain**.  
The agent behaves like a human evaluator: it generates topic-specific questions, accepts user answers, evaluates them using semantic similarity, provides feedback, and produces a final score out of **10**.

🔗 **Live demo:** https://evaluationagent-lf4rus2vzgtqdzuacm8muh.streamlit.app/

---

## 🔦 Highlights / Features

- Interactive, single-file Streamlit UI for running evaluations.
- Topic-driven question generation (you can type any topic).
- Human-in-the-loop flow: one question at a time, answer → evaluate → next question.
- Answer evaluation via embeddings + cosine similarity.
- Running total normalized to a **final score out of 10** with feedback summary.
- Conversation history view with expandable question/answer/evaluation items.
- Designed to be deployed easily on Streamlit Cloud.

---

## 📁 Project structure (typical)

```
Evaluation_Agent/
├── app.py                # Streamlit app entry (UI + orchestration)
├── state.py              # Typed State definition for LangGraph
├── nodes.py              # Graph nodes: chatbot, user_answer, evaluate_answer
├── maths.py              # embedding + similarity utilities
├── requirements.txt      # Python dependencies
├── .env                  # local environment variables (NOT in repo)
├── .gitignore
└── README.md
```

> Your project may have slightly different filenames (e.g., `main.py` or `app.py`). Use whatever file you run with `streamlit run <file>`.

---

## 🛠️ Prerequisites

- Python 3.9+ recommended
- `pip` (or an environment manager like `venv` / `conda`)
- API keys for model services (Groq, Hugging Face, LangSmith, Google Generative AI if used)

---

## ⚙️ Quick local setup

1. Clone repo
```bash
git clone https://github.com/Manish-Anchan/Evaluation_Agent.git
cd Evaluation_Agent
```

2. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate     # Windows PowerShell
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root (do **not** commit this file). Add your keys, for example:

```
GROQ_API_KEY=your_groq_api_key
HUGGINGFACEHUB_API_TOKEN=your_hf_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
```

5. Run the app
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 📦 Recommended `requirements.txt`

(Place this in your repo; you already have a generated list, but this covers the main imports used in the code.)

```
streamlit
python-dotenv
langchain
langchain-core
langchain-groq
langgraph
google-generativeai
huggingface-hub
groq
numpy
pydantic
```

> Tip: To freeze exact working versions after testing, run `pip freeze > requirements.txt`.

---

## 🚀 Deploying to Streamlit Cloud

1. Push your repo to GitHub (make sure `requirements.txt` & app file are present).
2. Go to https://streamlit.io/cloud and create a new app linked to your GitHub repo.
3. Set your repository file to the Streamlit entrypoint (e.g., `app.py`).
4. Add the environment variables via Streamlit Cloud UI (do **not** commit `.env`).
5. Deploy. Use **Manage app → Clear cache and reboot** if you change dependencies.

---

## 🧭 How to use the app (UI walkthrough)

1. Enter any topic in the sidebar input (default: "Machine Learning").
2. Click **Start Evaluation**.
3. Read each question shown in the main panel.
4. Type your answer and click **Submit Answer** (or **Skip**).
5. The app will evaluate your answer, show a similarity score and feedback, then continue to the next question.
6. At the end, the app normalizes the running score and shows the final score out of 10 plus a performance summary.
7. Use the **Conversation History** panel to expand previous Q&A and feedback items.

---

## 🔍 Troubleshooting

- **`ModuleNotFoundError: google.generativeai`**  
  Add `google-generativeai` to `requirements.txt` and re-deploy / reinstall:  
  `pip install google-generativeai`

- **Streamlit shows redacted error message & "original error message is redacted"**  
  Open Streamlit Cloud → Manage app → View logs to inspect full traceback.

- **Static / invisible text in question box (theme issues)**  
  The app forces dark text color in the question/answer boxes in CSS. If you still see invisible text, inspect the DOM with your browser developer tools — ensure the `.question-box` style is applied and contains the question string.

- **`.gitignore` changes not applied**  
  If `main` / `main.py` was already committed, run:
  ```bash
  git rm --cached main.py      # or `main` if no extension
  git add .gitignore
  git commit -m "Stop tracking main.py"
  git push origin main
  ```

- **Push rejected: non-fast-forward**  
  If you're certain the remote has no new useful commits, you can force-push:
  ```bash
  git push origin main --force
  ```
  Otherwise do:
  ```bash
  git pull origin main --rebase
  git push origin main
  ```

---

## ⚙️ Implementation notes (for maintainers)

- **Question generation** is produced by `ChatGroq` LLM in `nodes.py` (node `chatbot`).
- **Answer extraction** uses a small prompt to extract the canonical answer, then embeddings (Hugging Face inference client) compute similarity in `maths.py`.
- **Scoring** logic and thresholds are defined in `nodes.py` and can be tuned easily to change grading behavior or convert to raw scores.
- **State**: `state.py` contains a `TypedDict` definition used by LangGraph for `messages`, `topic`, `next_question`, and `count`.
- If you replace the embedding model or provider, update `maths.py` (embedding client and model name).

---

## 🛡 Security & privacy

- **Never commit** API keys or credentials. Use environment variables or the Streamlit Cloud secrets manager.
- The app may send user answers to external APIs (LLMs / embedding services). If you plan to collect sensitive personal data, do not send it to third-party APIs without consent.

---

## 🤝 Contributing

PRs welcome! If you want help:
- Open an issue describing your goal/bug.
- Attach logs or screenshots if things fail on Streamlit Cloud.
- For breaking changes to model providers, update `requirements.txt` and add migration notes in the changelog.

---

## 📜 License

MIT License — feel free to reuse and adapt.

---

## 💬 Contact

Made by **Manish**. Questions or want help customizing scoring, adding new providers (OpenAI / Anthropic / ElevenLabs TTS), or converting to a multi-user web app? Open an issue on the repo or reach out in the project chat.

---

Enjoy — and good luck with your evaluations! 🎯