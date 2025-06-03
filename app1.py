import streamlit as st
import openai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Hardcoded OpenRouter API key (replace with your actual key)
# OPENROUTER_API_KEY = "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"

# Configure OpenAI client to use OpenRouter

api_key = os.getenv("OPENROUTER_API_KEY")

openai.api_base = "https://openrouter.ai/api/v1"

def generate_professional_email(work_update, user_name, lead_name):
    """Generate professional email using OpenRouter endpoint."""
    try:
        prompt = f"""
Convert this work update into a professional email format:

Work Update: {work_update}

Format it as a professional daily progress email from {user_name} to {lead_name}.
Include:
- Professional greeting
- Clear subject line suggestion
- Well-structured content
- Professional closing

Keep it concise but professional.
"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or another model available via OpenRouter
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"OpenRouter Error: {e}")

def send_outlook_email(to_email, subject, body, from_email, password):
    """Send email through Outlook SMTP."""
    try:
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        raise RuntimeError(f"Email Error: {e}")

st.set_page_config(page_title="AI-Powered Email Generator", page_icon="✉️", layout="centered")
st.title("✉️ Generate & Send Professional Email via OpenRouter")

user_name = st.text_input("Your Name")
lead_name = st.text_input("Recipient Name")
to_email = st.text_input("Recipient Email")
subject = st.text_input("Email Subject (optional)", placeholder="Leave blank to auto-generate")
work_update = st.text_area("Work Update (what you accomplished today)")

st.markdown("---")
st.subheader("🔑 Outlook Credentials")
from_email = st.text_input("Your Outlook Email")
email_password = st.text_input("App Password", type="password")

if st.button("🚀 Generate & Send"):
    missing = []
    for name, value in [
        ("Your Name", user_name),
        ("Recipient Name", lead_name),
        ("Recipient Email", to_email),
        ("Work Update", work_update),
        ("Your Outlook Email", from_email),
        ("App Password", email_password)
    ]:
        if not value:
            missing.append(name)
    if missing:
        st.error(f"Please fill in: {', '.join(missing)}")
    else:
        try:
            with st.spinner("🤖 Generating email via OpenRouter..."):
                generated_email = generate_professional_email(work_update, user_name, lead_name)
            final_subject = subject.strip() or f"Daily Progress Update - {user_name}"
            st.markdown("**✏️ Generated Email Body:**")
            st.write(generated_email)

            with st.spinner("📤 Sending email..."):
                send_outlook_email(to_email, final_subject, generated_email, from_email, email_password)
            st.success("✅ Email sent successfully!")
        except Exception as e:
            st.error(str(e))
