# Client Query Management System (CQMS)

A Streamlit-based application for managing client queries with dedicated dashboards for **Clients**, **Support Users**, and **Admins**.  
This system ensures transparency, real-time availability tracking, and direct communication between support and admin.

---

## 🚀 Features

### Client Dashboard
- 👤 Client profile card (shows client name & role)
- 📋 View queries submitted by the client
- 📝 Submit new queries with email, mobile, heading, and description
- 🎯 Option to **assign query to a specific support user** OR submit as a **general query** (unassigned)

### Support Dashboard
- 👤 Support profile card (shows support name & role)
- 🎫 Ticket count with clickable view of assigned tickets
- 🟢/🔴 Availability toggle (sidebar)
- ❓ Ask Admin (submit doubts)
- 💬 Chat with Admin (sidebar)
- 📤 **Forward client queries to Admin** directly from single ticket view
- 📊 Metrics: Total, Open, Closed, In Progress, Overdue, Assigned
- 📈 Analytics: top support users, support group usage

### Admin Dashboard
- 📊 Metrics: Total, Open, Closed, In Progress
- 👥 Support availability tables (Available / Not Available)
- 📄 All tickets view with single/bulk update options
- 📈 Analytics: monthly query volume, status distribution, top support users, support group usage
- 📩 Doubts list from support users
- 💬 Chat messages from support users (including forwarded client queries)

---

## 🛠 Tech Stack
- **Python** (3.9+)
- **Streamlit** (UI framework)
- **Pandas** (data handling)
- **PostgreSQL** (optional DB integration, session-based fallback available)

---

## 📂 Project Structure
```
project_SN/
│
├── app.py / appX.py        # Main Streamlit app entry
├── utils/                  # Helper functions (DB connection, query handling)
├── dashboards/             # Client, Support, Admin dashboards
├── requirements.txt        # Dependencies
└── README.md               # Documentation
```

---

## ✨ Recent Enhancements
- Added **optional support assignment** in Client Dashboard (general queries possible).
- Support users can **forward client queries to Admin** from their dashboard.
- Improved success messages for clarity (assigned vs general queries).
- Enhanced metrics for Support Dashboard (overdue, assigned counts).

---

## 👨‍💻 Author
----------Created by **SholinganS**-----------

