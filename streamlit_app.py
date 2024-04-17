import openai
import streamlit as st
from openai import OpenAI

openai.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai.api_key)


def create_thread():
    return client.beta.threads.create()


def send_and_run(content):
    message = client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=content,
    )

    return client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant.id,
        stream=True,
    )


def wait_on_run(run):
    last_assistant_response = ""
    for chunk in run:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            last_assistant_response += content
            st.session_state.messages.append({"role": "assistant", "content": content})
            st.experimental_rerun()

    st.session_state.messages.append(
        {"role": "assistant", "content": last_assistant_response}
    )


assistant = client.beta.assistants.retrieve("asst_mLDWK2HsrZIK76mXL8xeFtHZ")
thread = create_thread()


def main():
    st.set_page_config(page_title="Chatbot App", page_icon=":robot_face:")
    st.title("Chatbot App")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = thread.id

    chat_container = st.container()

    user_input = st.chat_input("You:", placeholder="Type your message here...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        run = send_and_run(user_input)
        wait_on_run(run)

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


if __name__ == "__main__":
    main()
