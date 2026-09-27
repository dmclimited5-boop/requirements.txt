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
st.caption("PRINCE AI")


# ==========================================
# PRINCE CONFIG
# ==========================================

PRINCE_ENDPOINT = (
    "http://127.0.0.1:8090/v1/chat/completions"
)

PRINCE_API_KEY = st.secrets.get(
    "PRINCE_API_KEY",
    ""
).strip()


# ==========================================
# SESSION STATE
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ==========================================
# PRINCE API
# ==========================================

def call_prince(messages):

    if not PRINCE_API_KEY:
        raise ValueError(
            "PRINCE_API_KEY is missing from Streamlit Secrets."
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

    # Show useful API errors without exposing the key
    if not response.ok:
        try:
            error_data = response.json()
            raise RuntimeError(
                f"PRINCE API {response.status_code}: "
                f"{error_data}"
            )
        except ValueError:
            raise RuntimeError(
                f"PRINCE API {response.status_code}: "
                f"{response.text[:500]}"
            )

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]

    except (KeyError, IndexError, TypeError):
        raise RuntimeError(
            f"Unexpected PRINCE response: {data}"
        )


# ==========================================
# CHAT
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


prompt = st.chat_input(
    "Talk to PRINCE..."
)


if prompt:

    user_message = {
        "role": "user",
        "content": prompt
    }

    st.session_state.messages.append(
        user_message
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("PRINCE is thinking..."):

            try:

                reply = call_prince(
                    st.session_state.messages
                )

                st.markdown(reply)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply
                })

            except Exception as error:

                st.error(
                    f"❌ PRINCE Error: {error}"
                )


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.header("👑 PRINCE STATUS")

    if PRINCE_API_KEY:
        st.success("PRC API Key: Loaded")
    else:
        st.error("PRC API Key: Missing")

    st.write(
        "Endpoint:"
    )

    st.code(
        "127.0.0.1:8090"
    )

    st.divider()

    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []

        st.rerun()

"requirements.txt"

:::writing{variant="document" id="81502" title="PRINCE Requirements"}

streamlit
requests

Streamlit Secrets

Only add:

PRINCE_API_KEY = "YOUR_NEW_PRC_KEY"

This version uses PRINCE as the only AI.

One thing to watch for: because you're deploying Streamlit, if you get connection refused / connection timeout, that doesn't mean the PRC key is wrong. It means Streamlit Cloud cannot reach "127.0.0.1:8090" on your Android.
