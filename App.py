import streamlit as st
import requests

# ==========================================
# PAGE
# ==========================================

st.set_page_config(
    page_title="DMC EMPIRE CHAT BOT",
    page_icon="👑",
    layout="centered"
)

st.title("👑 DMC EMPIRE CHAT BOT")
st.caption("Universal Design")


# ==========================================
# CONFIG
# ==========================================

PRINCE_ENDPOINT = (
    "http://127.0.0.1:8090/v1/chat/completions"
)

PRINCE_API_KEY = st.secrets.get(
    "PRINCE_API_KEY",
    ""
).strip()

GOOGLE_KEYS = [
    st.secrets.get("GOOGLE_API_KEY_1", ""),
    st.secrets.get("GOOGLE_API_KEY_2", ""),
    st.secrets.get("GOOGLE_API_KEY_3", "")
]

GOOGLE_KEYS = [
    key.strip()
    for key in GOOGLE_KEYS
    if key and key.strip()
]


# ==========================================
# SESSION STATE
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "provider" not in st.session_state:
    st.session_state.provider = "—"

if "google_key_index" not in st.session_state:
    st.session_state.google_key_index = 0


# ==========================================
# PRINCE
# ==========================================

def call_prince(messages):

    if not PRINCE_API_KEY:
        raise ValueError(
            "PRINCE API key is missing."
        )

    headers = {
        "Authorization": f"Bearer {PRINCE_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "prince",
        "messages": messages
    }

    response = requests.post(
        PRINCE_ENDPOINT,
        headers=headers,
        json=payload,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]


# ==========================================
# GEMINI REST API
# ==========================================

def call_gemini(messages):

    if not GOOGLE_KEYS:
        raise ValueError(
            "No Google API keys configured."
        )

    index = (
        st.session_state.google_key_index
        % len(GOOGLE_KEYS)
    )

    api_key = GOOGLE_KEYS[index]

    st.session_state.google_key_index += 1

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.8-flash:generateContent"
    )

    contents = []

    for message in messages:

        if message["role"] == "user":
            role = "user"
        else:
            role = "model"

        contents.append({
            "role": role,
            "parts": [
                {
                    "text": message["content"]
                }
            ]
        })

    payload = {
        "contents": contents
    }

    response = requests.post(
        url,
        params={
            "key": api_key
        },
        headers={
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    try:
        return (
            data["candidates"][0]
            ["content"]["parts"][0]["text"]
        )

    except (KeyError, IndexError, TypeError):

        raise ValueError(
            f"Unexpected Gemini response: {data}"
        )


# ==========================================
# ROUTER
# ==========================================

def get_response(user_input):

    messages = (
        st.session_state.messages
        + [
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    # --------------------------------------
    # PRINCE FIRST
    # --------------------------------------

    if PRINCE_API_KEY:

        try:

            reply = call_prince(messages)

            return reply, "PRINCE"

        except Exception as error:

            st.toast(
                "PRINCE unavailable → Gemini fallback",
                icon="⚠️"
            )

    # --------------------------------------
    # GEMINI
    # --------------------------------------

    try:

        reply = call_gemini(messages)

        return reply, "Gemini"

    except Exception as error:

        return (
            f"❌ AI Error: {str(error)}",
            "Error"
        )


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.header("👑 System Status")

    st.write(
        f"**Current AI:** "
        f"`{st.session_state.provider}`"
    )

    st.write(
        f"**Google Keys Loaded:** "
        f"`{len(GOOGLE_KEYS)}`"
    )

    st.write(
        "**PRINCE Cloud:** "
        "`127.0.0.1:8090`"
    )

    st.divider()

    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []

        st.session_state.provider = "—"

        st.session_state.google_key_index = 0

        st.rerun()


# ==========================================
# CHAT HISTORY
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )


# ==========================================
# CHAT INPUT
# ==========================================

prompt = st.chat_input(
    "Talk to PRINCE..."
)

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner(
            "PRINCE is thinking..."
        ):

            reply, provider = get_response(
                prompt
            )

            st.session_state.provider = provider

            st.markdown(reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })
