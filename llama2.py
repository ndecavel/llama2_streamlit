import streamlit as st
import openai

st.title("AnyScale Llama 2 Chatbot")

st.sidebar.header("Configuration")

# Initial setup for conversation state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = ""
    st.session_state.readable_history = ""
    st.session_state.started = False
    st.session_state.system_prompt = "You are a helpful assistant."
    st.session_state.temperature = 0.0
    st.session_state.api_key = ""
    st.session_state.max_tokens = 200
    st.session_state.user_input = ""

# Sidebar for system prompt, temperature, max tokens, and API key
if not st.session_state.started:
    st.session_state.system_prompt = st.sidebar.text_area("System Prompt:", st.session_state.system_prompt, height=150, help='Do not include any <s> or <<SYS>> tags with the system prompt. This is done in the backend.')
    st.session_state.temperature = st.sidebar.slider("Temperature:", 0.0, 1.0, st.session_state.temperature, 0.05, help="Set the randomness of the model's responses. Lower values make it more deterministic.")
    st.session_state.max_tokens = st.sidebar.number_input("Max Tokens:", value=st.session_state.max_tokens, step=1, help="Set the maximum length of the response in terms of tokens.")
    st.session_state.api_key = st.sidebar.text_input("API Key:", value=st.session_state.api_key, type="password")

    
    if st.sidebar.button("START") and st.session_state.api_key:
        st.session_state.started = True
        st.session_state.conversation_history = f"<s>[INST] <<SYS>> {st.session_state.system_prompt} <</SYS>>"
        openai.api_base = "https://api.endpoints.anyscale.com/v1"
        openai.api_key = st.session_state.api_key
else:
    st.sidebar.text("System Prompt:")
    st.sidebar.text(st.session_state.system_prompt)
    st.sidebar.text("Temperature:")
    st.sidebar.write(st.session_state.temperature)
    st.sidebar.text("Max Tokens:")
    st.sidebar.write(st.session_state.max_tokens)
    st.sidebar.text("API Key:")
    st.sidebar.write("•" * len(st.session_state.api_key))
    if st.sidebar.button("RESET"):
        st.session_state.started = False
        st.session_state.conversation_history = ""
        st.session_state.readable_history = ""
        if hasattr(st.session_state, "last_user_input"):
            del st.session_state.last_user_input


def get_response(prompt, temperature, max_tokens):
    response = openai.Completion.create(
        model="meta-llama/Llama-2-70b-chat-hf",
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].text.strip()


if st.session_state.started:

    if 'user_input_value' not in st.session_state:
        st.session_state.user_input_value = ""

    if 'input_key' not in st.session_state:
        st.session_state.input_key = 0
    
    # User input
    user_input = st.text_area("You:", key=st.session_state.input_key, help='Do not include any [INST] tags with the user input. This is done in the backend.')  # Changed from st.text_input for consistency


    if st.button("Submit"):  # Add a Submit button
        if user_input and (not hasattr(st.session_state, "last_user_input") or user_input != st.session_state.last_user_input):
            st.session_state.last_user_input = user_input
            user_input = user_input.strip()

            if '[/INST]' not in st.session_state.conversation_history:
                st.session_state.conversation_history += f" {user_input} [/INST]"
            else:
                st.session_state.conversation_history += f"<s> [INST] {user_input} [/INST]"
            st.session_state.readable_history += f"You: {user_input}\n\n"

            with st.spinner("Fetching response..."):
                response = get_response(st.session_state.conversation_history, st.session_state.temperature, st.session_state.max_tokens)
                st.session_state.conversation_history += f' {response} </s>'

            st.session_state.readable_history += f"AI Tutor: {response}\n\n"
            
            # Clear the user input for the next time
            if user_input:
                st.session_state.input_key += 1

    col1, col2 = st.columns(2)

    col1.text_area("Conversation:", st.session_state.readable_history, height=400, key="readable_hist")
    col2.text_area("Raw History:", st.session_state.conversation_history, height=400, key="raw_hist")

    if st.button("Show Info"):
        info_text = f"""
**System Prompt:** 
{st.session_state.system_prompt}

**Temperature:** 
{st.session_state.temperature}

**Max Tokens:** 
{st.session_state.max_tokens}

**Readable History:**
```
{st.session_state.readable_history}
```

**Conversation History:**
```
{st.session_state.conversation_history}
```
"""
        st.markdown(info_text)
