import streamlit as st
import pandas as pd
from datetime import datetime
import os
from supabase import create_client

st.set_page_config(page_title="ENTERPRISE HRMS v8 – PRO MAX", layout="wide")

# ================= SUPABASE CONNECTION ================= #

SUPABASE_URL = "bpxpyfbsfigicwijtwpp"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJweHB5ZmJzZmlnaWN3aWp0d3BwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI2MTA2ODAsImV4cCI6MjA4ODE4NjY4MH0.mQ_2pKOB0Uvt5INeukAV8P4_yrKiHWq1rPjsx41MXrQ"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= SESSION ================= #

if "user" not in st.session_state:
    st.session_state.user = None

# ================= LOGIN ================= #

def login():
    st.title("🔐 ENTERPRISE HRMS v8 – PRO MAX")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        response = supabase.table("users").select("*")\
            .eq("username", username)\
            .eq("password", password)\
            .execute()

        if response.data:
            user = response.data[0]
            st.session_state.user = {"username": user["username"], "role": user["role"]}
            st.rerun()
        else:
            st.error("Invalid Credentials")

def logout():
    st.session_state.user = None
    st.rerun()

# ================= DASHBOARD ================= #

def dashboard():
    response = supabase.table("candidates").select("*").execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        st.info("No Candidates Yet")
        return

    col1,col2,col3,col4,col5 = st.columns(5)
    col1.metric("Total", len(df))
    col2.metric("Freshers", len(df[df['type']=="Fresher"]))
    col3.metric("Experience", len(df[df['type']=="Experience"]))
    col4.metric("Selected", len(df[df['status']=="Selected"]))
    col5.metric("Rejected", len(df[df['status']=="Rejected"]))

# ================= HR PANEL ================= #

def hr_panel():
    st.sidebar.write(f"Logged in as: {st.session_state.user['username']}")
    if st.sidebar.button("Logout"):
        logout()

    st.title("👨‍💼 HR PANEL")
    dashboard()

    st.subheader("Add Candidate")

    name = st.text_input("Full Name")
    mobile = st.text_input("Mobile")
    email = st.text_input("Email")
    type_ = st.radio("Type", ["Fresher","Experience"], horizontal=True)
    designation = st.text_input("Designation")
    branch = st.text_input("Branch")
    division = st.text_input("Division")

    experience_years = ""
    current_salary = ""
    expected_salary = ""

    if type_ == "Experience":
        experience_years = st.text_input("Experience Years")
        current_salary = st.text_input("Current Salary")
        expected_salary = st.text_input("Expected Salary")

    if st.button("Save Candidate", use_container_width=True):

        supabase.table("candidates").insert({
            "name": name,
            "mobile": mobile,
            "email": email,
            "type": type_,
            "designation": designation,
            "branch": branch,
            "division": division,
            "experience_years": experience_years,
            "current_salary": current_salary,
            "expected_salary": expected_salary,
            "status": "Pending",
            "created_by": st.session_state.user['username'],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }).execute()

        st.success("Candidate Saved Successfully")
        st.rerun()

    response = supabase.table("candidates").select("*").execute()
    df = pd.DataFrame(response.data)
    st.dataframe(df, use_container_width=True)

# ================= AGM PANEL ================= #

def agm_panel():
    st.sidebar.write(f"Logged in as: {st.session_state.user['username']}")
    if st.sidebar.button("Logout"):
        logout()

    st.title("🏢 AGM PANEL")
    dashboard()

    response = supabase.table("candidates").select("*").execute()
    df = pd.DataFrame(response.data)

    for i,row in df.iterrows():
        with st.expander(f"{row['name']} - {row['designation']}"):

            st.write("Status:", row['status'])

            if st.button("Select", key=f"s{i}"):
                supabase.table("candidates").update(
                    {"status":"Selected"}
                ).eq("id",row["id"]).execute()
                st.rerun()

            if st.button("Reject", key=f"r{i}"):
                supabase.table("candidates").update(
                    {"status":"Rejected"}
                ).eq("id",row["id"]).execute()
                st.rerun()

# ================= ADMIN PANEL ================= #

def admin_panel():
    st.sidebar.write("Logged in as: Admin")
    if st.sidebar.button("Logout"):
        logout()

    st.title("⚙ ADMIN PANEL")

    username = st.text_input("Username")
    password = st.text_input("Password")
    role = st.selectbox("Role", ["HR","AGM"])

    if st.button("Create User", use_container_width=True):
        supabase.table("users").insert({
            "username": username,
            "password": password,
            "role": role
        }).execute()

        st.success("User Created")

# ================= MAIN ================= #

if not st.session_state.user:
    login()
else:
    role = st.session_state.user['role']
    if role == "HR":
        hr_panel()
    elif role == "AGM":
        agm_panel()
    elif role == "Admin":
        admin_panel()