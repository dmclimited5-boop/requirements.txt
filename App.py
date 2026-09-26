import streamlit as st
import requests
import google.generativeai as genai

# PRINCE API key
PRINCE_API_KEY = st.secrets.get("PRINCE_API_KEY", "")

if not PRINCE_API_KEY:
    st.warning("PRINCE API key is not configured.")

# ──────────────────────────────────────────────
# PAGE SETUP
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="DMC EMPIRE CHAT BOT",
    page_icon="👑",
    layout="centered"
)

st.title("👑 DMC EMPIRE CHAT BOT")
st.caption("Universal Design")


# ──────────────────────────────────────────────
# SECRETS
# ──────────────────────────────────────────────
try:
    PRINCE_API_KEY = st.secrets.get(
        "PRINCE_API_KEY",
        ""
    )

    GOOGLE_KEYS = [
        st.secrets.get("GOOGLE_API_KEY_1", ""),
        st.secrets.get("GOOGLE_API_KEY_2", ""),
        st.secrets.get("GOOGLE_API_KEY_3", ""),
    ]

    GOOGLE_KEYS = [
        key.strip()
        for key in GOOGLE_KEYS
        if key.strip()
    ]

except Exception:
    st.error("⚠️ Please configure your Streamlit Secrets.")
    st.stop()


# ──────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "provider" not in st.session_state:
    st.session_state.provider = "—"

if "google_key_index" not in st.session_state:
    st.session_state.google_key_index = 0


# ──────────────────────────────────────────────
# PRINCE API
# ──────────────────────────────────────────────
def call_prince(messages):

    if not PRINCE_API_KEY:
        raise ValueError("PRINCE API key is missing.")

    # Connect your existing PRINCE/PRM
    # implementation here.

    raise RuntimeError(
        "PRINCE API connector is not connected."
    )


# ──────────────────────────────────────────────
# GEMINI
# ──────────────────────────────────────────────
def call_gemini(messages):

    if not GOOGLE_KEYS:
        raise ValueError("No Google API keys found.")

    key = GOOGLE_KEYS[
        st.session_state.google_key_index
        % len(GOOGLE_KEYS)
    ]

    st.session_state.google_key_index += 1

    client = genai.Client(
        api_key=key
    )

    # Convert conversation history into
    # a format Gemini can understand.
    conversation = []

    for msg in messages:

        role = (
            "User"
            if msg["role"] == "user"
            else "Assistant"
        )

        conversation.append(
            f"{role}: {msg['content']}"
        )

    prompt = "\n\n".join(conversation)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


# ──────────────────────────────────────────────
# AI ROUTER
# ──────────────────────────────────────────────
def get_response(user_input):

    messages = (
        st.session_state.messages
        + [{
            "role": "user",
            "content": user_input
        }]
    )

    # PRINCE FIRST
    try:

        reply = call_prince(messages)

        return reply, "PRINCE"

    except Exception:

        st.toast(
            "PRINCE unavailable → Gemini Flash",
            icon="⚠️"
        )

    # GEMINI FALLBACK
    try:

        reply = call_gemini(messages)

        return reply, "Gemini Flash"

    except Exception as e:

        return (
            f"❌ AI Error: {e}",
            "Error"
        )


# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:

    st.header("👑 PRINCE SYSTEM")

    st.write(
        f"**Current AI:** `{st.session_state.provider}`"
    )

    st.write(
        f"**Google Keys:** `{len(GOOGLE_KEYS)}`"
    )

    if PRINCE_API_KEY:
        st.success("PRINCE API: READY")
    else:
        st.warning("PRINCE API: KEY MISSING")

    st.divider()

    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []

        st.rerun()


# ──────────────────────────────────────────────
# CHAT HISTORY
# ──────────────────────────────────────────────
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])


# ──────────────────────────────────────────────
# CHAT INPUT
# ──────────────────────────────────────────────
if prompt := st.chat_input("Talk to PRINCE..."):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("PRINCE is thinking..."):

            reply, provider = get_response(prompt)

            st.session_state.provider = provider

            st.markdown(reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })
