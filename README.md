Client Query Management System (CQMS)
=====================================

Overview
--------
CQMS is a Streamlit-based portal for managing client queries with three roles:
- Client
- Support
- Admin

All data (users, queries, chat, doubts, availability) is stored in PostgreSQL for persistence.

Features
--------
1. Client Dashboard
   - View own queries
   - Submit new queries
   - Profile card with login/logout times

2. Support Dashboard
   - Profile card
   - Toggle availability (persistent in Postgres)
   - View assigned tickets
   - Submit doubts to Admin (persistent in Postgres)
   - Chat with Admin (persistent in Postgres)
   - Ticket management (single/bulk update)
   - Analytics (top support users, support group usage)

3. Admin Dashboard
   - Metrics: total, open, closed, in progress
   - View support availability (from Postgres)
   - View chat messages (from Postgres)
   - View doubts (from Postgres)
   - Ticket management (single/bulk update)
   - Analytics: monthly query volume, status distribution, top support users, group usage

Database Schema
---------------
Tables required:
- users
- queries
- support_chat
- support_doubts
- support_availability

See schema.sql for CREATE TABLE statements.

Setup
-----
1. Install dependencies:
   pip install streamlit psycopg2-binary pandas python-dotenv

2. Configure environment variables (.env):
   PG_HOST=localhost
   PG_PORT=5432
   PG_DB=CQMS
   PG_USER=postgres
   PG_PASSWORD=yourpassword

3. Initialize database:
   Run schema.sql in PostgreSQL.

4. Run the app:
   streamlit run app.py

Usage
-----
- Clients log in, submit queries, and track their own tickets.
- Support users log in, toggle availability, manage assigned tickets, chat with Admin, and submit doubts.
- Admins log in, view all tickets, support availability, chat messages, doubts, and analytics.

Notes
-----
- Availability, chat, and doubts are persisted in Postgres.
- Queries are tracked with status and priority.
- Analytics charts are generated directly in Streamlit.

Author
------
Developed by Sholingan.
