import streamlit as st
import requests

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="DMC EMPIRE CHAT BOT",
    page_icon="👑",
    layout="centered"
)

st.title("👑 DMC EMPIRE CHAT BOT")
st.caption("Universal Design")


# ==========================================
# CONFIGURATION
# ==========================================

PRINCE_ENDPOINT = "http://127.0.0.1:8090/v1/chat/completions"

try:
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

except Exception as error:
    st.error("⚠️ Please configure your API keys in Streamlit Secrets.")
    st.stop()


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
# PRINCE API
# ==========================================

def call_prince(messages):

    if not PRINCE_API_KEY:
        raise ValueError("PRINCE API key is missing.")

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

    try:
        return data["choices"][0]["message"]["content"]

    except (KeyError, IndexError, TypeError):
        raise ValueError(
            f"Unexpected PRINCE response: {data}"
        )


# ==========================================
# GEMINI FALLBACK
# ==========================================

def call_gemini(messages):

    if not GOOGLE_KEYS:
        raise ValueError(
            "No Google API keys configured."
        )

    # Modern Google GenAI SDK
    from google import genai as google_genai

    key_index = (
        st.session_state.google_key_index
        % len(GOOGLE_KEYS)
    )

    api_key = GOOGLE_KEYS[key_index]

    st.session_state.google_key_index += 1

    client = google_genai.Client(
        api_key=api_key
    )

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

    prompt = "\n".join(conversation)

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    if not response.text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    return response.text


# ==========================================
# RESPONSE ROUTER
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
    # TRY PRINCE FIRST
    # --------------------------------------

    if PRINCE_API_KEY:

        try:

            reply = call_prince(messages)

            return reply, "PRINCE"

        except Exception:

            st.toast(
                "PRINCE unavailable → Switching to Gemini",
                icon="⚠️"
            )

    # --------------------------------------
    # GEMINI FALLBACK
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
# DISPLAY CHAT HISTORY
# ==========================================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(
            msg["content"]
        )


# ==========================================
# CHAT INPUT
# ==========================================

prompt = st.chat_input(
    "Talk to PRINCE..."
)

if prompt:

    # Add user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # Display user message
    with st.chat_message("user"):

        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):

        with st.spinner(
            "PRINCE is thinking..."
        ):

            reply, provider = get_response(
                prompt
            )

            st.session_state.provider = provider

            st.markdown(reply)

    # Save assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": reply
        }
    )
