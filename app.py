import streamlit as st
import psycopg2
import pandas as pd
import hashlib
from datetime import datetime
import os
from dotenv import load_dotenv
import numpy as np

# -------------------- Row color helper --------------------
def color_status(val):
    if val == "Open":
        return "background-color:#D6EAF8; color:#154360;"   # Blue shades
    elif val == "In Progress":
        return "background-color:#FAD7A0; color:#7D6608;"   # Orange shades
    elif val == "Closed":
        return "background-color:#D5F5E3; color:#145A32;"   # Green shades
    return ""

# =====================================================
# LOAD ENV
# =====================================================
load_dotenv()

# =====================================================
# DB CONNECTION
# =====================================================
def get_connection():
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", "5432"),
        database=os.getenv("PG_DB", "CQMS"),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD", "123")
    )

# =====================================================
# PASSWORD HASH
# =====================================================
def make_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =====================================================
# SAFE PRIORITY INDEX
# =====================================================
def safe_priority_index(value):
    priorities = ["Low", "Medium", "High"]
    return priorities.index(value) if value in priorities else 1

# =====================================================
# AUTH FUNCTIONS
# =====================================================
def authenticate_user(username, password, role):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM users
        WHERE username=%s AND hashed_password=%s AND role=%s
    """, (username.strip(), make_hash(password), role))
    res = cur.fetchone()
    conn.close()
    return res is not None

def register_user(username, password, role):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO users (username, hashed_password, role)
            VALUES (%s,%s,%s)
        """, (username.strip(), make_hash(password), role))
        conn.commit()
    except Exception:
        conn.rollback()
        raise ValueError("Username already exists or invalid input")
    finally:
        conn.close()

def reset_password(username, password, role):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET hashed_password=%s
        WHERE username=%s AND role=%s
    """, (make_hash(password), username.strip(), role))
    conn.commit()
    conn.close()

# =====================================================
# QUERY FUNCTIONS
# =====================================================
def submit_query(username, email, mobile, heading, desc):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO queries
        (username, mail_id, mobile_number, query_heading,
         query_description, status, priority, query_created_time)
        VALUES (%s,%s,%s,%s,%s,'Open','Medium',%s)
    """, (username, email, mobile, heading, desc, datetime.now()))
    conn.commit()
    conn.close()

def get_queries():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM queries ORDER BY query_created_time DESC", conn)
    conn.close()
    return df

def update_ticket(qid, status, heading, desc, priority, assigned_to=None):
    conn = get_connection()
    cur = conn.cursor()
    if assigned_to:
        cur.execute("""
            UPDATE queries
            SET status=%s,
                query_heading=%s,
                query_description=%s,
                priority=%s,
                assigned_to=%s,
                query_closed_time = CASE WHEN %s='Closed' THEN %s ELSE query_closed_time END
            WHERE query_id=%s
        """, (status, heading, desc, priority, assigned_to, status, datetime.now(), qid))
    else:
        cur.execute("""
            UPDATE queries
            SET status=%s,
                query_heading=%s,
                query_description=%s,
                priority=%s,
                query_closed_time = CASE WHEN %s='Closed' THEN %s ELSE query_closed_time END
            WHERE query_id=%s
        """, (status, heading, desc, priority, status, datetime.now(), qid))
    conn.commit()
    conn.close()

# =====================================================
# SIDEBAR
# =====================================================
def sidebar_logout():
    with st.sidebar:
        st.markdown("### 🔐 Account")
        if st.button("🚪 Logout", key="logout_button"):
            if st.session_state.get("role") == "Support":
                st.session_state.support_logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.clear()
            st.rerun()

# =====================================================
# STYLES
# =====================================================
def set_styles():
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    header, footer, #MainMenu {visibility:hidden;}
    .stApp {background:#F4F6F7;}
    .login-card {max-width:850px; border-radius:12px; background:white; box-shadow:0 6px 16px rgba(0,0,0,.2);}
    .header-box {background:#6a0dad; color:white; text-align:center; padding:20px; font-size:1.6rem; font-weight:bold;}
    .form-box {background:#ECF0F1; padding:30px;}
    .stButton button {background:#3498DB; color:white; font-weight:bold; width:100%; border-radius:6px;}
    </style>
    """, unsafe_allow_html=True)

# =====================================================
# LOGIN PAGE
# =====================================================
def login_page():
    set_styles()
    col1, col2 = st.columns([1,1])

    with col1:
        st.image("https://img.freepik.com/free-vector/man-explaining-chart-woman-working-with-laptop_1262-19826.jpg", width=600)

    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="header-box">Client Query Management System</div>', unsafe_allow_html=True)
        st.markdown('<div class="form-box">', unsafe_allow_html=True)

        t1, t2, t3 = st.tabs(["Login", "Register", "Forgot Password"])

        with t1:
            u = st.text_input("Username", key="login_u")
            p = st.text_input("Password", type="password", key="login_p")
            r = st.selectbox("Role", ["Client","Support","Admin"], key="login_r")
            if st.button("LOG IN", key="btn_login"):
                if authenticate_user(u,p,r):
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.role = r
                    if r == "Support":
                        st.session_state.support_login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        with t2:
            ru = st.text_input("New Username", key="reg_u")
            rp = st.text_input("New Password", type="password", key="reg_p")
            rr = st.selectbox("Role", ["Client","Support","Admin"], key="reg_r")
            if st.button("Register", key="btn_register"):
                try:
                    register_user(ru, rp, rr)
                    st.success("User registered successfully")
                except Exception as e:
                    st.error(str(e))

        with t3:
            fu = st.text_input("Username", key="fp_u")
            fr = st.selectbox("Role", ["Client","Support","Admin"], key="fp_r")
            fp = st.text_input("New Password", type="password", key="fp_p")
            if st.button("Reset Password", key="btn_reset"):
                reset_password(fu, fp, fr)
                st.success("Password reset successful")

        st.markdown("</div></div>", unsafe_allow_html=True)
# =====================================================
# CLIENT DASHBOARD
# =====================================================
def client_dashboard():
    st.header("📞 Client Dashboard")

    # Show client profile name
    client_name = st.session_state.username
    st.markdown(f"""
        <div style="background:#2E86C1; padding:15px; border-radius:8px; color:white; font-size:18px;">
            👤 <b>{client_name}</b><br>
            Role: Client
        </div>
    """, unsafe_allow_html=True)

    # Show login/logout times
    if "client_login_time" in st.session_state:
        st.info(f"Login Time: {st.session_state.client_login_time}")
    if "client_logout_time" in st.session_state:
        st.info(f"Last Logout Time: {st.session_state.client_logout_time}")

    # -------------------- Client tickets view --------------------
    df = get_queries()
    if "created_by" in df.columns:
        my_queries = df[df["created_by"] == client_name]
        st.subheader("📋 Your Queries")
        if not my_queries.empty:
            st.dataframe(my_queries.style.applymap(color_status, subset=["status"]), use_container_width=True)
        else:
            st.info("No queries submitted yet.")

    # -------------------- Submit new query --------------------
    st.markdown("---")
    st.subheader("📝 Submit Query")

    email = st.text_input("Email", key="client_email")
    mobile = st.text_input("Mobile", key="client_mobile")
    heading = st.text_input("Heading", key="client_heading")
    desc = st.text_area("Description", key="client_desc")

    if st.button("Submit Query", key="btn_submit_query"):
        submit_query(client_name, email, mobile, heading, desc)
        st.success("Query submitted successfully")

# =====================================================
# SUPPORT DASHBOARD
# =====================================================
def support_dashboard():
    st.header("🛠 Support Dashboard")

    # Profile section
    support_name = st.session_state.username
    st.markdown(f"""
        <div style="background:#75BFEC; padding:15px; border-radius:8px; color:white; font-size:18px;">
            👤 <b>{support_name}</b><br>
            Role: Support
        </div>
    """, unsafe_allow_html=True)
    # -------------------- Availability toggle --------------------
    with st.sidebar:
        st.markdown("### 👤 Support Availability")
        if "support_available" not in st.session_state:
            st.session_state.support_available = True  # default

        status = "🟢 Available" if st.session_state.support_available else "🔴 Not Available"
        st.info(f"{support_name} is currently {status}")

        if st.button("Toggle Availability"):
            st.session_state.support_available = not st.session_state.support_available
            st.rerun()
    # -------------------- Chat with Admin (Sidebar) --------------------
    with st.sidebar:
        st.markdown("### 💬 Chat with Admin")

        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

        chat_input = st.text_area("Type your message")
        if st.button("Send to Admin"):
            if chat_input.strip():
                st.session_state.chat_messages.append({
                    "from": support_name,
                    "to": "Admin",
                    "message": chat_input
                })
                st.success("Message sent to Admin.")
            else:
                st.warning("Please enter a valid message.")


    # Show login/logout times
    if "support_login_time" in st.session_state:
        st.info(f"Login Time: {st.session_state.support_login_time}")
    if "support_logout_time" in st.session_state:
        st.info(f"Last Logout Time: {st.session_state.support_logout_time}")

        # Ticket count for this support user
    df = get_queries()
    if "assigned_to" in df.columns:
        my_tickets = df[df["assigned_to"] == support_name]
        ticket_count = len(my_tickets)

        if st.button(f"🎫 You have {ticket_count} tickets assigned. Click to view"):
            st.subheader(f"Tickets assigned to {support_name}")
            st.dataframe(my_tickets.style.applymap(color_status, subset=["status"]), use_container_width=True)
# -------------------- Ask Admin Section --------------------
    st.markdown("---")
    st.subheader("❓ Ask Admin")

    doubt_text = st.text_area("Enter your doubt/question for Admin")
    if st.button("Submit to Admin"):
        if doubt_text.strip():
            if "support_doubts" not in st.session_state:
                st.session_state.support_doubts = []
            st.session_state.support_doubts.append({
                "user": support_name,
                "doubt": doubt_text
            })
            st.success("Your doubt has been sent to Admin.")
        else:
            st.warning("Please enter a valid doubt before submitting.")


    if df.empty:
        st.info("No tickets available")
        return

    # Summary metrics
    df["query_created_time"] = pd.to_datetime(df.get("query_created_time"), errors="coerce")
    total_count = len(df)
    open_count = (df["status"] == "Open").sum()
    closed_count = (df["status"] == "Closed").sum()
    inprogress_count = (df["status"] == "In Progress").sum()
    overdue_count = ((pd.Timestamp.now() - df["query_created_time"]) > pd.Timedelta(hours=42)).sum()
    assigned_count = df["assigned_to"].notna().sum() if "assigned_to" in df.columns else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📊 Total", total_count)
    c2.metric("📂 Open", open_count)
    c3.metric("✅ Closed", closed_count)
    c4.metric("🔄 In Progress", inprogress_count)
    c5.metric("⏱ Overdue", overdue_count)
    st.metric("👨‍💻 Assigned", assigned_count)

    # Filters
    status_filter = st.selectbox("Status Filter", ["All","Open","In Progress","Closed"])
    filtered_df = df if status_filter=="All" else df[df["status"]==status_filter]

    # Table with row colors
    st.dataframe(filtered_df.style.applymap(color_status, subset=["status"]), use_container_width=True)

    # Tabs
    st.markdown("---")
    tab1, tab2 = st.tabs(["✏️ Single Ticket", "📦 Bulk Update"])

    # Support users list
    conn = get_connection()
    support_users = pd.read_sql("SELECT username FROM users WHERE role='Support'", conn)["username"].tolist()
    conn.close()

    # Tab1: Single
    with tab1:
        ticket_ids = filtered_df["query_id"].astype(str).tolist()
        if ticket_ids:
            qid = st.selectbox("Select Ticket ID", ticket_ids)
            row = filtered_df[filtered_df["query_id"].astype(str)==qid].iloc[0]
            st.text_input("Heading", value=row.query_heading, disabled=True)
            st.text_area("Description", value=row.query_description, disabled=True)
            status = st.selectbox("Status", ["Open","In Progress","Closed"], index=["Open","In Progress","Closed"].index(row.status))
            priority = st.selectbox("Priority", ["Low","Medium","High"], index=safe_priority_index(row.priority))
            assigned_to = st.selectbox("Assign To", support_users) if support_users else None
            if st.button("Update Ticket"):
                update_ticket(qid, status, row.query_heading, row.query_description, priority, assigned_to)
                st.success("Ticket updated")
                st.rerun()

    # Tab2: Bulk
    with tab2:
        selected_ids = st.multiselect("Select Ticket IDs", filtered_df["query_id"].astype(str).tolist())
        if selected_ids:
            status_bulk = st.selectbox("Bulk Status", ["Open","In Progress","Closed"])
            priority_bulk = st.selectbox("Bulk Priority", ["Low","Medium","High"])
            assigned_bulk = st.selectbox("Bulk Assign To", support_users) if support_users else None
            if st.button("Apply Bulk Update"):
                for qid in selected_ids:
                    row = filtered_df[filtered_df["query_id"].astype(str)==qid].iloc[0]
                    update_ticket(qid, status_bulk, row.query_heading, row.query_description, priority_bulk, assigned_bulk)
                st.success(f"Updated {len(selected_ids)} tickets")
                st.rerun()

    # -------------------- Analytics --------------------
    st.markdown("---")
    st.subheader("📊 Support analytics")

    if "assigned_to" in df.columns:
        top_support = df[df["assigned_to"].notna()].groupby("assigned_to").size().reset_index(name="count")
        top_support = top_support.sort_values("count", ascending=False).head(10)
        st.markdown("#### 👨‍💻 Top support users")
        st.bar_chart(top_support.set_index("assigned_to"))

    if "support_group" in df.columns:
        group_usage = df.groupby("support_group").size().reset_index(name="count")
        group_usage = group_usage.sort_values("count", ascending=False)
        st.markdown("#### 🧩 Support group usage")
        st.bar_chart(group_usage.set_index("support_group"))


# =====================================================
# ADMIN DASHBOARD
# =====================================================
def admin_dashboard():
    st.header("👑 Admin Dashboard")

    df = get_queries()
    if df.empty:
        st.info("No tickets available")
        return
    # -------------------- Chat messages from Support --------------------
    st.markdown("---")
    st.subheader("💬 Chat from Support Users")

    if "chat_messages" in st.session_state and st.session_state.chat_messages:
        chat_df = pd.DataFrame(st.session_state.chat_messages)
        st.table(chat_df)
    else:
        st.info("No chat messages from support users yet.")


    # Summary metrics
    df["query_created_time"] = pd.to_datetime(df.get("query_created_time"), errors="coerce")
    total_count = len(df)
    open_count = (df["status"] == "Open").sum()
    closed_count = (df["status"] == "Closed").sum()
    inprogress_count = (df["status"] == "In Progress").sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 Total", total_count)
    c2.metric("📂 Open", open_count)
    c3.metric("✅ Closed", closed_count)
    c4.metric("🔄 In Progress", inprogress_count)

    # -------------------- Support users availability --------------------
    st.subheader("👥 Support Users Availability")

    if "availability_status" in st.session_state:
        status_dict = st.session_state.availability_status

        # Available users
        available_users = [u for u,s in status_dict.items() if s=="Available"]
        st.markdown("#### 🟢 Available Support Users")
        if available_users:
            st.table(pd.DataFrame(available_users, columns=["username"]))
        else:
            st.info("No support users are currently available.")

        # Not Available users
        not_available_users = [u for u,s in status_dict.items() if s=="Not Available"]
        st.markdown("#### 🔴 Not Available Support Users")
        if not_available_users:
            st.table(pd.DataFrame(not_available_users, columns=["username"]))
        else:
            st.info("All support users are available.")
    else:
        st.info("No availability support users now.")
# -------------------- Support Doubts Section --------------------
    st.markdown("---")
    st.subheader("📩 Doubts from Support Users")

    if "support_doubts" in st.session_state and st.session_state.support_doubts:
        doubts_df = pd.DataFrame(st.session_state.support_doubts)
        st.table(doubts_df)
    else:
        st.info("No doubts submitted by support users yet.")


    # -------------------- Tickets table --------------------
    st.subheader("📄 All Tickets")
    st.dataframe(df.style.applymap(color_status, subset=["status"]), use_container_width=True)

    # Tabs
    st.markdown("---")
    tab1, tab2 = st.tabs(["✏️ Single Ticket", "📦 Bulk Update"])

    # Tab1: Single
    with tab1:
        ticket_ids = df["query_id"].astype(str).tolist()
        if ticket_ids:
            qid = st.selectbox("Select Ticket ID", ticket_ids)
            row = df[df["query_id"].astype(str)==qid].iloc[0]
            heading = st.text_input("Heading", value=row.query_heading)
            desc = st.text_area("Description", value=row.query_description)
            status = st.selectbox("Status", ["Open","In Progress","Closed"], index=["Open","In Progress","Closed"].index(row.status))
            priority = st.selectbox("Priority", ["Low","Medium","High"], index=safe_priority_index(row.priority))
            if st.button("Apply Changes"):
                update_ticket(qid, status, heading, desc, priority)
                st.success("Ticket updated")
                st.rerun()

    # Tab2: Bulk
    with tab2:
        selected_ids = st.multiselect("Select Ticket IDs", df["query_id"].astype(str).tolist())
        if selected_ids:
            status_bulk = st.selectbox("Bulk Status", ["Open","In Progress","Closed"])
            priority_bulk = st.selectbox("Bulk Priority", ["Low","Medium","High"])
            if st.button("Apply Bulk Update"):
                for qid in selected_ids:
                    row = df[df["query_id"].astype(str)==qid].iloc[0]
                    update_ticket(qid, status_bulk, row.query_heading, row.query_description, priority_bulk)
                st.success(f"Bulk updated {len(selected_ids)} tickets")
                st.rerun()

    # -------------------- Analytics --------------------
    st.markdown("---")
    st.subheader("📊 Admin analytics")

    if "query_created_time" in df.columns:
        monthly = df.copy()
        monthly["month"] = monthly["query_created_time"].dt.strftime("%b")
        monthly_stats = monthly.groupby("month").size().reset_index(name="count")
        st.markdown("#### 📅 Monthly query volume")
        st.line_chart(monthly_stats.set_index("month"))

    status_stats = df["status"].value_counts().reset_index()
    status_stats.columns = ["status", "count"]
    st.markdown("#### 📌 Status distribution")
    st.bar_chart(status_stats.set_index("status"))

    if "assigned_to" in df.columns:
        top_support = df[df["assigned_to"].notna()].groupby("assigned_to").size().reset_index(name="count")
        top_support = top_support.sort_values("count", ascending=False).head(10)
        st.markdown("#### 👨‍💻 Top support users")
        st.bar_chart(top_support.set_index("assigned_to"))

    if "support_group" in df.columns:
        group_usage = df.groupby("support_group").size().reset_index(name="count")
        group_usage = group_usage.sort_values("count", ascending=False)
        st.markdown("#### 🧩 Support group usage")
        st.bar_chart(group_usage.set_index("support_group"))

# =====================================================
# MAIN
# =====================================================
def main():
    st.set_page_config("CQMS Portal", layout="wide")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        sidebar_logout()
        role = st.session_state.get("role", "Client")
        if role == "Client":
            client_dashboard()
        elif role == "Support":
            support_dashboard()
        elif role == "Admin":
            admin_dashboard()
    else:
        login_page()

if __name__ == "__main__":
    main()
