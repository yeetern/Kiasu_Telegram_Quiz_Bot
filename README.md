# Kiasu Telegram Quiz Bot (Project Kancil)

> **Safe to fail, optimized to learn.**  
> An open-source Telegram quiz bot designed for SPM students.

---

## 📌 Overview

**Kiasu Telegram Quiz Bot** is an open-source educational Telegram bot built for Malaysian **SPM students**, focusing on **low-pressure practice**, **active recall** and **instructional feedback**.

Unlike traditional quiz bots that only show scores, this project is designed to:

- Support students who are **afraid to answer publicly**
- Turn mistakes into **guided learning opportunities**
- Bridge the gap between **practice questions and textbooks**
- Demonstrate **production-quality backend engineering** in an EdTech context

---

## 🎯 Core Philosophy

> **Fail safely → Get feedback → Return to textbook → Reinforce learning**

- Failure should be safe and private  
- Every mistake should come with feedback  
- Feedback must point back to the learning source  
- Learning quality matters more than rankings  

---

## ✨ Key Features

### ✅ Private 1-to-1 Practice (Sprint 1 – MVP)
- Students interact with the bot via **private chat**
- MCQ format (A / B / C / D)
- Immediate correctness feedback after submission
- Automatic instructional references (subject, chapter, page, note)

Example feedback:
```
❌ Incorrect
Correct answer: C
📘 Reference: Physics Form 4, Chapter 2, Page 123
💡 Newton’s Second Law: F = ma
```


---

### 🧠 Instructional Feedback System (Core Feature)
Each question can be linked to structured metadata:
- Subject (Physics, Chemistry, Add Math, etc.)
- Level (Form 4 / Form 5)
- Chapter / Topic
- Textbook page number
- Short conceptual explanation

Mistakes are treated as **entry points for learning**, not penalties.

---

## 🚧 Project Status

🚧 **Work in Progress — Sprint 1**

Current focus:
- Private (DM) practice workflow
- Single-question interaction
- Stable and reproducible development environment

---

## 🧩 Tech Stack

| Layer | Technology |
|---|---|
| Bot Framework | Python 3.11 + aiogram 3.x |
| Database | PostgreSQL 16 |
| Containerization | Docker & Docker Compose |
| State (MVP) | In-memory FSM |
| Deployment | Polling (Webhook deferred) |

---

## 🏗️ Design Principles

- Simple first, scalable later  
- Avoid premature abstraction  
- Clear scope per sprint  
- Engineering discipline over quick scripts  

---

## 🗂️ Project Structure

```text
Kiasu_Telegram_Quiz_Bot/
├── .env.example        # Environment variable template
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── README.md
└── src/
    ├── main.py         # Application entry point
    ├── config.py       # Configuration loader
    ├── database.py    # Database connection
    ├── handlers/      # Telegram handlers
    ├── models/        # Database models
    └── services/      # Business logic
```

---

## ▶️ Quickstart (Local Development)
### 1️⃣ Requirements
- Docker & Docker Compose
- Telegram Bot Token (via @BotFather)
### 2️⃣ Environment Setup
```bash
cp .env.example .env
# Fill in your BOT_TOKEN
```
### 3️⃣ Run the Project
```bash
docker compose up --build
```
### 4️⃣ Test the Bot
Open Telegram and send:
```bash
/start
```

---

## 🧪 Roadmap
### Sprint 1 – Private Practice MVP
- Private chat practice
- Single question per session
- Instructional reference feedback
### Sprint 2 – Group Session Mode
- Timed group quizzes
- Delayed result reveal
- Top-3 leaderboard only (no public error list)
### Sprint 3 – Learning Analytics
- Subject-level performance tracking
- Weak-topic detection
- Exportable learning summaries

---

## ⚖️ Copyright & Ethics
- This repository does not include any past-year exam papers
- No copyrighted images are stored
- Only Telegram file_id / message_id references are saved
- The bot acts as a learning index and feedback system, not a content host

---

## 🔐 Privacy
- No phone numbers are collected
- Only Telegram user IDs are used
- No personal performance data is publicly exposed
- Future leaderboards will display anonymous or top-ranked results only

---

## 🤝 Contributing
Contributions via Issues, Discussions, and Pull Requests are welcome.

Please ensure:
- Clear and readable code
- Alignment with the project’s learning-first philosophy
- No features beyond the current sprint scope

---

## 📜 License

MIT License

You are free to use, modify, and redistribute this project with attribution.

---

## 🙏 Acknowledgement

This project aims to provide SPM students with a learning environment that:
- Does not shame mistakes
- Encourages attempts
- Respects individual learning pace