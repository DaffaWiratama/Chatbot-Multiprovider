import streamlit as st
import requests
from openai import OpenAI

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "Chatbot sederhana yang dapat membantu menjawab pertanyaan Anda menggunakan berbagai model bahasa."
    "Pilih penyedia di bawah ini dan berikan kunci API yang sesuai. "
)    
    
st.write("[WARNING] Maaf saat ini hanya mendukung penyedia Groq. ")
st.write("Kami mendukung penggunaan bahasa Indonesia")
st.write("DaffaWiratama - 2025 (Bagian dari pengembangan Streamlit)")
# Choose provider
provider = st.selectbox("Provider", ["Groq"])

# Provider-specific inputs
if provider == "OpenAI":
    openai_api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        key="openai_api_key"
    )
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.", icon="🗝️")
        st.stop()

    client = OpenAI(api_key=openai_api_key)

else:
    groq_api_key = st.text_input(
        "Groq API Key",
        value="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",
        key="groq_api_key"
    )
    groq_base_url = st.text_input(
        "Groq API Base URL",
        value="https://api.groq.com/openai/v1",
        key="groq_base_url"
    )

    # Model dropdown (ONLY CHANGE REQUESTED)
    groq_model = st.selectbox(
        "Groq Model",
        [
            "allam-2-7b",
            "groq/compound",
            "groq/compound-mini",
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "meta-llama/llama-guard-4-12b",
            "meta-llama/llama-prompt-guard-2-22m",
            "meta-llama/llama-prompt-guard-2-86m",
            "moonshotai/kimi-k2-instruct",
            "moonshotai/kimi-k2-instruct-0905",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "openai/gpt-oss-safeguard-20b",
            "qwen/qwen3-32b",
        ],
        key="groq_model",
    )

    if not groq_api_key:
        st.info("Please add your Groq API key to continue.", icon="🗝️")
        st.stop()


def _extract_text_from_response(json_obj):
    if not json_obj:
        return ""
    if isinstance(json_obj, dict):
        for key in ("output", "text", "content", "message"):
            if key in json_obj and isinstance(json_obj[key], str):
                return json_obj[key]
        choices = json_obj.get("choices") or json_obj.get("generations")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                for k in ("text", "message", "content"):
                    if k in first and isinstance(first[k], str):
                        return first[k]
                msg = first.get("message") or first.get("content")
                if isinstance(msg, str):
                    return msg
    return str(json_obj)


def call_groq(api_key: str, messages: list, model: str, base_url: str) -> str:
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    content = getattr(response.choices[0].message, "content", None)
    if content is None:
        obj = response.to_dict() if hasattr(response, "to_dict") else response
        return _extract_text_from_response(obj) or ""
    return content

# ------------------------------
# Chat UI
# ------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if provider == "OpenAI":
        try:
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages,
                stream=True,
            )
        except Exception as e:
            st.error("OpenAI request failed. Verify your API key and model.")
            with st.expander("OpenAI error details"):
                st.text(str(e))
            response = ""
        else:
            with st.chat_message("assistant"):
                response = st.write_stream(stream)

    else:
        try:
            response = call_groq(
                groq_api_key,
                st.session_state.messages,
                model=groq_model,
                base_url=groq_base_url,
            )
        except Exception as e:
            st.error("Groq request failed.")
            with st.expander("Groq error details"):
                st.text(str(e))
            response = ""

        with st.chat_message("assistant"):
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})