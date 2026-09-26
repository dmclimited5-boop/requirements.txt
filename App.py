import streamlit as st
import requests
import google.generativeai as genai

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DMC EMPIRE CHAT BOT",
    page_icon="👑",
    layout="centered"
)

st.title("👑 DMC EMPIRE CHAT BOT")
st.caption("Universal Design")


# ============================================================
# SECRETS
# ============================================================

PRINCE_API_KEY = st.secrets.get(
    "PRINCE_API_KEY",
    ""
)

GOOGLE_KEYS = [
    st.secrets.get("GOOGLE_API_KEY_1", ""),
    st.secrets.get("GOOGLE_API_KEY_2", ""),
    st.secrets.get("GOOGLE_API_KEY_3", "")
]

GOOGLE_KEYS = [
    key.strip()
    for key in GOOGLE_KEYS
    if key.strip()
]


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "provider" not in st.session_state:
    st.session_state.provider = "—"

if "google_key_index" not in st.session_state:
    st.session_state.google_key_index = 0


# ============================================================
# PRINCE API
# ============================================================

def call_prince(messages):

    if not PRINCE_API_KEY:
        raise ValueError(
            "PRINCE API key is not configured."
        )

    # --------------------------------------------------------
    # PRINCE API CONNECTOR
    #
    # Your PRINCE API implementation goes here.
    #
    # The API key is already loaded securely from:
    #
    # st.secrets["PRINCE_API_KEY"]
    #
    # --------------------------------------------------------

    raise RuntimeError(
        "PRINCE API connector is not configured yet."
    )


# ============================================================
# GEMINI FALLBACK
# ============================================================

def call_gemini(messages):

    if not GOOGLE_KEYS:
        raise ValueError(
            "No Google API keys are configured."
        )

    key_index = (
        st.session_state.google_key_index
        % len(GOOGLE_KEYS)
    )

    key = GOOGLE_KEYS[key_index]

    st.session_state.google_key_index += 1

    genai.configure(
        api_key=key
    )

    model = genai.GenerativeModel(
        "gemini-3.6-flash"
    )

    history = []

    for message in messages[:-1]:

        role = (
            "user"
            if message["role"] == "user"
            else "model"
        )

        history.append({
            "role": role,
            "parts": [
                message["content"]
            ]
        })

    chat = model.start_chat(
        history=history
    )

    response = chat.send_message(
        messages[-1]["content"]
    )

    return response.text


# ============================================================
# AI ROUTER
# ============================================================

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

    # --------------------------------------------------------
    # PRINCE FIRST
    # --------------------------------------------------------

    try:

        reply = call_prince(
            messages
        )

        return reply, "PRINCE"

    except Exception:

        st.toast(
            "PRINCE unavailable → Gemini fallback",
            icon="⚠️"
        )

    # --------------------------------------------------------
    # GEMINI FALLBACK
    # --------------------------------------------------------

    try:

        reply = call_gemini(
            messages
        )

        return reply, "Gemini"

    except Exception as error:

        return (
            f"❌ AI Error: {error}",
            "Error"
        )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("👑 PRINCE SYSTEM")

    st.write(
        f"**Current AI:** "
        f"`{st.session_state.provider}`"
    )

    st.write(
        f"**Gemini Keys:** "
        f"`{len(GOOGLE_KEYS)}`"
    )

    st.divider()

    if PRINCE_API_KEY:

        st.success(
            "PRINCE API KEY: LOADED"
        )

    else:

        st.warning(
            "PRINCE API KEY: MISSING"
        )

    if GOOGLE_KEYS:

        st.success(
            "GEMINI: READY"
        )

    else:

        st.warning(
            "GEMINI: NO KEYS"
        )

    st.divider()

    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []

        st.session_state.provider = "—"

        st.rerun()


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input(
    "Talk to PRINCE..."
)

if prompt:

    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):

        st.markdown(prompt)

    # --------------------------------------------------------
    # AI RESPONSE
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "PRINCE is thinking..."
        ):

            reply, provider = get_response(
                prompt
            )

            st.session_state.provider = (
                provider
            )

            st.markdown(reply)

    # --------------------------------------------------------
    # SAVE RESPONSE
    # --------------------------------------------------------

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })
