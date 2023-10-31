import streamlit as st

st.title("Literature Condenser 📚")
st.text("Upload all relevant PDF files from the sidebar.\nAsk any Qs about the PDFs.")
st.text("Happy literature reviewing :)")

# "with" notation
with st.sidebar:
    uploaded_files = st.file_uploader("Select all files you want to interact with", type = "pdf", accept_multiple_files = True)

# Initialise chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask something"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = f"Your mum"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})