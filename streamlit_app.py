import openai
import time
import streamlit as st
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

openai.api_key = st.secrets["OPENAI_API_KEY"]
# Import necessary libraries

# Initialize OpenAI client with your API key
client = OpenAI(
    api_key=openai.api_key,
)


# Function to get the response from a thread
def get_response():
    """
    This function retrieves the messages from a thread in ascending order.
    Parameters:
    thread (Thread): The thread to retrieve messages from.
    """
    return client.beta.threads.messages.list(
        thread_id=st.session_state.thread_id, order="asc"
    )


# Function to create a thread
def create_thread():
    """
    This function creates a new thread.
    """
    thread = client.beta.threads.create()
    return thread


def send_and_run(content):
    """
    This function sends a message to the thread and runs it.
    Parameters:
    content (str): The content of the message to send.
    """
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
    while run.status == "queued" or run.status == "in_progress":
        try:
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id,
            )
            print(run.status)
            time.sleep(0.5)
        except openai.NotFoundError:
            # If the run is not found, create a new run
            run = send_and_run(st.session_state.messages[-1]["content"])
            print("Created new run:", run.id)
    return run


# Create an assistant and thread
assistant = client.beta.assistants.retrieve("asst_mLDWK2HsrZIK76mXL8xeFtHZ")
thread = create_thread()


# Streamlit app
def main():
    st.set_page_config(page_title="Chatbot App", page_icon=":robot_face:")
    st.title("Chatbot App")

    # Initialize chat history and thread ID
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = thread.id

    # Create a container for the chat history
    chat_container = st.container()

    # Get user input
    user_input = st.chat_input("You:")

    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Waiting for response..."):
            # Send user input to the chatbot and get response
            run = wait_on_run(send_and_run(user_input))
            response = get_response()

            # Find the last assistant response
            last_assistant_response = None
            for message in reversed(response.data):
                if message.role == "assistant":
                    for content in message.content:
                        if content.type == "text":
                            last_assistant_response = content.text.value
                            break
                if last_assistant_response:
                    break

            if last_assistant_response:
                # Update the last assistant response in the chat history
                st.session_state.messages.append(
                    {"role": "assistant", "content": last_assistant_response}
                )

    # Display the chat history in the container
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


if __name__ == "__main__":
    main()
