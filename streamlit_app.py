import streamlit as st
import requests
from openai import OpenAI

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that can use OpenAI or Groq (Llama 4) to generate responses. "
    "Pick a provider below and supply the corresponding API key. "
    "You can also learn how to build LLM apps step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Choose provider
provider = st.selectbox("Provider", ["OpenAI", "Groq"])

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
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
        type="password",
        key="groq_api_key"
    )
    groq_base_url = st.text_input(
        "Groq API Base URL",
        value="https://api.groq.ai/v1",
        key="groq_base_url"
    )
    groq_model = st.text_input(
        "Groq Model",
        value="llama-4",
        key="groq_model"
    )
    if not groq_api_key:
        st.info("Please add your Groq API key to continue.", icon="🗝️")
        st.stop()

    # Create an OpenAI client.

    # Groq provider inputs
    

def _extract_text_from_response(json_obj):
    """Try a few common response shapes and return the first text found."""
    if not json_obj:
        return ""
    # Common fields
    if isinstance(json_obj, dict):
        for key in ("output", "text", "content", "message"):
            if key in json_obj and isinstance(json_obj[key], str):
                return json_obj[key]
        # choices -> first -> text / message
        choices = json_obj.get("choices") or json_obj.get("generations")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                for k in ("text", "message", "content"):
                    if k in first and isinstance(first[k], str):
                        return first[k]
                # nested message { 'content': '...' }
                msg = first.get("message") or first.get("content")
                if isinstance(msg, str):
                    return msg
    # Fallback to stringified JSON
    return str(json_obj)


def call_groq(api_key: str, messages: list, model: str = "llama-4", base_url: str = "https://api.groq.ai/v1") -> str:
    """Send a simple conversation to Groq and return the generated text.

    This is a lightweight, tolerant client that tries a few common Groq endpoints
    and response shapes. Adjust if your Groq tenancy requires a different path.
    """
    # Build a prompt from the conversation (simple concatenation)
    prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"input": prompt}

    endpoints = [
        f"{base_url}/models/{model}/generate",
        f"{base_url}/models/{model}:generate",
        f"{base_url}/models/{model}/completions",
        f"{base_url}/completions",
    ]

    errors = []
    for url in endpoints:
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
        except Exception as e:
            # network error, collect and try next
            errors.append(f"{url} -> exception: {e}")
            continue

        if resp.status_code in (200, 201):
            try:
                j = resp.json()
            except Exception:
                return resp.text or ""
            text = _extract_text_from_response(j)
            return text
        else:
            # collect truncated body to help debugging
            body = resp.text or ""
            snippet = body if len(body) < 1000 else body[:1000] + "...[truncated]"
            errors.append(f"{url} -> status {resp.status_code}: {snippet}")

    # If every attempt failed, raise a helpful error that includes attempted endpoints and responses
    msg = "Failed to get a successful response from Groq API. Tried endpoints:\n" + "\n".join(errors)
    raise RuntimeError(msg)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if provider == "OpenAI":
            # Generate a response using the OpenAI API.
            try:
                stream = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                )

            except Exception as e:
                msg = str(e)
                st.error("OpenAI request failed. Verify your API key and model.")
                with st.expander("OpenAI error details"):
                    st.text(msg)
                response = ""
                st.session_state.messages.append({"role": "assistant", "content": response})

            else:
                # Stream the response to the chat using `st.write_stream`, then store it in
                # session state.
                with st.chat_message("assistant"):
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})

        else:
            # Call Groq API (non-streaming implementation)
            try:
                response = call_groq(groq_api_key, st.session_state.messages, model=groq_model, base_url=groq_base_url)
            except Exception as e:
                msg = str(e)
                # Provide a friendly summary and surface detailed info in an expander
                suggestion = "Check your Groq API key, base URL, and model name."
                if "401" in msg or "Unauthorized" in msg:
                    suggestion = "Authentication failed (401). Verify your Groq API key."
                elif "404" in msg or "Not Found" in msg:
                    suggestion = "Endpoint not found (404). Check base URL and model name."
                elif "exception:" in msg:
                    suggestion = "Network error contacting Groq. Check network and base URL."

                st.error(f"Groq request failed. {suggestion}")
                with st.expander("Groq error details"):
                    st.text(msg)
                response = ""

            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
