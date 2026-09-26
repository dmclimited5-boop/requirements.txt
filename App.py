import streamlit as st
from google import genai

st.set_page_config(
    page_title="DMC EMPIRE CHAT BOT",
    page_icon="👑",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #211900, #070707 40%, #000);
    color: white;
}

.title {
    text-align: center;
    color: #d4af37;
    font-size: 44px;
    font-weight: 900;
    text-shadow: 0 0 25px #d4af37;
}

.subtitle {
    text-align: center;
    color: #aaa;
    margin-bottom: 30px;
}

.status {
    text-align: center;
    padding: 14px;
    margin-bottom: 20px;
    border: 1px solid #5c4b12;
    border-radius: 12px;
    background: rgba(212,175,55,.06);
}

[data-testid="stSidebar"] {
    background: #050505;
}

.stButton button {
    border: 1px solid #d4af37;
    color: #d4af37;
    background: #111;
    border-radius: 10px;
}

.stButton button:hover {
    background: #d4af37;
    color: #000;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="title">👑 DMC EMPIRE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">PRINCE AI COMMAND INTERFACE</div>',
    unsafe_allow_html=True
)

PRINCE_API_KEY = st.secrets.get("PRINCE_API_KEY", "")

GOOGLE_KEYS = [
    st.secrets.get("GOOGLE_API_KEY_1", ""),
    st.secrets.get("GOOGLE_API_KEY_2", ""),
    st.secrets.get("GOOGLE_API_KEY_3", ""),
    st.secrets.get("GOOGLE_API_KEY_4", ""),
    st.secrets.get("GOOGLE_API_KEY_5", "")
]

GOOGLE_KEYS = [
    key.strip()
    for key in GOOGLE_KEYS
    if key and key.strip()
]

if "messages" not in st.session_state:
    st.session_state.messages = []

if "google_key_index" not in st.session_state:
    st.session_state.google_key_index = 0

if "provider" not in st.session_state:
    st.session_state.provider = "READY"


def call_prince(messages):
    if not PRINCE_API_KEY:
        raise Exception("PRINCE API key is missing.")

    # PRINCE API connection goes here.
    # The API endpoint/protocol has not been supplied,
    # so no fake endpoint is used.

    raise Exception(
        "PRINCE API connection is not configured."
    )


def call_gemini(messages):

    if not GOOGLE_KEYS:
        raise Exception(
            "No Google API key is configured."
        )

    key = GOOGLE_KEYS[
        st.session_state.google_key_index
        % len(GOOGLE_KEYS)
    ]

    st.session_state.google_key_index += 1

    client = genai.Client(api_key=key)

    conversation = []

    for message in messages:

        role = message["role"]
        content = message["content"]

        if role == "user":
            name = "User"
        else:
            name = "Assistant"

        conversation.append(
            f"{name}: {content}"
        )

    prompt = "\n\n".join(conversation)

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    if not response.text:
        raise Exception(
            "Gemini returned an empty response."
        )

    return response.text


def get_ai_response(user_input):

    messages = (
        st.session_state.messages
        + [{
            "role": "user",
            "content": user_input
        }]
    )

    # Try PRINCE first
    try:

        answer = call_prince(messages)

        st.session_state.provider = "PRINCE"

        return answer

    except Exception:

        pass

    # Gemini fallback
    try:

        answer = call_gemini(messages)

        st.session_state.provider = "Gemini"

        return answer

    except Exception as error:

        st.session_state.provider = "ERROR"

        return (
            "❌ AI ERROR\n\n"
            + str(error)
        )


with st.sidebar:

    st.markdown("## 👑 PRINCE CONTROL")

    st.write(
        "**AI:** "
        + st.session_state.provider
    )

    if PRINCE_API_KEY:
        st.success("PRINCE KEY: LOADED")
    else:
        st.warning("PRINCE KEY: MISSING")

    if GOOGLE_KEYS:
        st.success(
            f"GOOGLE KEYS: {len(GOOGLE_KEYS)}"
        )
    else:
        st.warning("GOOGLE KEYS: NONE")

    st.divider()

    if st.button(
        "🗑️ CLEAR CHAT",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


st.markdown(
    f"""
    <div class="status">
        👑 <b>PRINCE SYSTEM</b><br>
        API KEY:
        {"READY" if PRINCE_API_KEY else "NOT CONFIGURED"}
        <br>
        GEMINI:
        {"READY" if GOOGLE_KEYS else "NOT CONFIGURED"}
    </div>
    """,
    unsafe_allow_html=True
)


for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message("user"):
            st.write(message["content"])

    else:

        with st.chat_message("assistant"):
            st.write(message["content"])


user_input = st.chat_input(
    "Talk to PRINCE..."
)


if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):

        with st.spinner(
            "PRINCE is processing..."
        ):

            answer = get_ai_response(
                user_input
            )

        st.write(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

And your "requirements.txt" should be exactly:

:::writing{variant="document" id="29574" title="requirements.txt — Ready to Copy"}

streamlit
google-genai

Put both files directly in the repository root:

App.py
requirements.txt

Then add your new/rotated PRINCE key and Google key through Streamlit Secrets rather than putting the keys inside "App.py".
