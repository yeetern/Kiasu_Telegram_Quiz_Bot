# 🐿️ Kiasu Telegram Quiz Bot

### *Project Kancil — Safe to Fail, Optimized to Learn*

> **This is not a quiz bot.
> This is a private, failure-safe learning system — disguised as a Telegram bot.**

An open-source educational platform designed for **SPM students**, where **mistakes are expected, private and instructional**.

---

## 🌱 Why Project Kancil Exists

Most digital quiz systems are built around **competition, exposure and ranking**.
They optimize for speed and scores — **not understanding**.

Project Kancil takes a different stance:
> **Learning does not require public failure.
> It requires safe attempts and meaningful feedback.**

This project was built to answer one question:
> *How can we turn every wrong answer into a constructive learning event — without shame, pressure or surveillance?*

---

## 🧠 Core Learning Philosophy

### **Attempt → Fail Safely → Receive Feedback → Reinforce via Reference**

* **Private by Default**
  All practice happens in 1-to-1 chats. No public leaderboards. No social comparison.

* **Failure as a Feature**
  A wrong answer is not an endpoint — it is the *entry point* to explanation.

* **Contextual Reinforcement**
  Every mistake is followed by:
  * *Why it is wrong*
  * *Where to relearn it* (Subject · Chapter · Page / Hint)

This design is inspired by **formative assessment**, not exam ranking.

---

## 🎓 Who This Is For

* **SPM students** who want to practice without fear
* **Educators** who want to distribute guided practice safely
* **Schools / NGOs** looking for low-friction, privacy-first learning tools
* **Developers** interested in FSM-driven, async, production-grade bot architecture

---

## ✨ What Makes This Different

### 🛠️ Educator-First Quiz Creation

* Create quizzes **directly inside Telegram**
* Upload:

  * Text questions **or**
  * Screenshot/photo-based questions
* Define:

  * Correct option
  * Instructional hint or reference
* Generate a **deep link** for instant student access

  ```
  t.me/yourbot?start=quiz_id
  ```

No dashboards. No LMS setup. No accounts.

---

### ✅ Student Practice Experience

* **One question at a time**
* **Immediate feedback**
* **Private mistakes**
* **Actionable hints instead of penalties**

Students engage with *understanding*, not anxiety.

---

## 🔍 How It Works (Conceptual Flow)

```text
Educator creates quiz
 → Bot stores structured question data
 → Deep link is generated
 → Student opens link (private chat)
 → Question is delivered
 → Student answers
 → Bot returns:
      ✓ Correct / ✗ Incorrect
      + Explanation / Hint
 → Learning reinforced safely
```

No public records. No exposure. No shaming.

---

## 🧩 Why Telegram?

Telegram is chosen **deliberately**, not accidentally.

* **Private by Design** — 1-to-1 chats reduce fear of failure
* **Low Barrier** — no login, no new app, no device requirements
* **Excellent Media Handling** — ideal for image-based questions
* **Accessible** — works well in low-resource and mobile-first environments

Telegram is not used for virality —
it is used for **frictionless, private learning**.

---

## 🏗️ Technical Architecture (Production-Grade)

| Layer            | Technology                          |
| ---------------- | ----------------------------------- |
| Bot Framework    | **Aiogram 3.x** (Async, modern FSM) |
| Database         | **PostgreSQL 16**                   |
| ORM              | **SQLAlchemy 2.0 (Async)**          |
| State Management | Aiogram FSM (Redis-ready)           |
| Deployment       | Docker & Docker Compose             |

### Engineering Principles

* Explicit state transitions (FSM)
* Async I/O end-to-end
* Clear separation of creation vs attempt flows
* No business logic in handlers without state control

This is **not** a toy bot.

---

## 🔐 Privacy & Ethics (Non-Negotiable)

* ❌ No phone numbers collected
* ❌ No personal identifiers beyond Telegram user ID
* ❌ No exam papers stored
* ❌ No copyrighted images hosted

Only **Telegram `file_id` references** are saved.
The system acts as a **learning index**, not a content host.

---

## 🚫 Non-Goals (What This Project Will Never Be)

To avoid misuse and scope creep:

* ❌ Not a content hosting platform
* ❌ Not a public ranking or leaderboard system
* ❌ Not an exam paper distributor
* ❌ Not a surveillance or performance tracking tool

Learning > metrics.

---

## 🧪 Roadmap

### Sprint 1 — Private Practice MVP ✅

* Private 1-to-1 quiz sessions
* Immediate feedback with instructional hints

### Sprint 2 — Group Learning (Carefully Designed)

* Timed group sessions
* Delayed result reveal
* **Top-3 only**, no public error lists

### Sprint 3 — Learning Analytics (Ethical)

* Subject-level weakness detection
* Personal progress summaries
* Exportable reports for *students*, not rankings

---

## 🤝 Contributing

Contributions are welcome — **with constraints**.

Please ensure:

* Code clarity over cleverness
* Alignment with learning-first philosophy
* No features that increase pressure, exposure or shame

If a feature makes students afraid to try — it does not belong here.

---

## 📜 License

MIT License
Free to use, modify, and redistribute with attribution.

---

## 🙏 Closing Note

Project Kancil exists for one reason:

> **To give students permission to try, fail and learn — quietly, safely and honestly.**

If this project helps even one student attempt a question they were afraid of — it has already succeeded.

---