import openai
import time
import streamlit as st
from openai import OpenAI

openai.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai.api_key)


def get_response():
    return client.beta.threads.messages.list(
        thread_id=st.session_state.thread_id, order="asc"
    )


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
    )


def wait_on_run(run):
    while run.status in ["queued", "in_progress"]:
        try:
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id,
            )
            time.sleep(0.5)
        except openai.NotFoundError:
            run = send_and_run(st.session_state.messages[-1]["content"])
    return run


assistant = client.beta.assistants.retrieve("asst_mLDWK2HsrZIK76mXL8xeFtHZ")
thread = create_thread()


def main():
    st.set_page_config(page_title="Chatbot App", page_icon=":robot_face:")
    st.title("Relationship Design Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = thread.id

    chat_container = st.container()
    user_input = st.chat_input("Write your message here:")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Waiting for response..."):
            run = wait_on_run(send_and_run(user_input))
            response = get_response()

            for message in reversed(response.data):
                if message.role == "assistant":
                    for content in message.content:
                        if content.type == "text":
                            last_assistant_response = content.text.value
                            st.session_state.messages.append(
                                {
                                    "role": "assistant",
                                    "content": last_assistant_response,
                                }
                            )
                            break
                if last_assistant_response:
                    break

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


if __name__ == "__main__":
    main()
