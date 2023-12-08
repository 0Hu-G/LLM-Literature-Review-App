import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv, find_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import FAISS
import urllib, urllib.request
import feedparser

load_dotenv(find_dotenv())

st.set_page_config(page_title = 'Revis.io', 
                    page_icon = '📚', layout = 'wide', initial_sidebar_state = 'auto')

st.title("Revis.io 📚")
st.text("Upload all relevant PDF files from the sidebar.\nAsk any Qs about the PDFs.")
st.text("Happy literature reviewing :)")

if "conversation" not in st.session_state:
    st.session_state.conversation = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = None

if user_question := st.chat_input("Ask something..."):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # st.session_state.messages.append({"role": "system", "content": system_template})
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_question)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_question})

    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response['answer'])
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response['answer']})

# "with" notation
with st.sidebar:
    st.subheader("Upload Documents")
    uploaded_files = st.file_uploader("Select all files you want to interact with", type = "pdf", accept_multiple_files = True)
    
    st.markdown("<h3 style='font-size: 16px; color: rgb(255, 255, 255);'>or</h3>", unsafe_allow_html=True)

    st.subheader("Search arXiv")
    
    search_text = str(st.text_input("""Enter research area and the number of papers you want to retreive.
                                Use the following format:\n e.g. 'natural language processing, 3'""", placeholder="Topic of interest"))
    
    max_results = -1  # Initialize max_results to indicate no specific value provided yet

    if search_text and len(search_text) > 0:
        max_results_candidate = search_text[-1]
        if max_results_candidate.isdigit():
            max_results = int(max_results_candidate)

    # Assign a default value if max_results is still -1
    if max_results == -1:
        max_results = 5  # Default value of 10 (change it to an appropriate value)
    
    st.markdown("<h3 style='font-size: 16px; color: rgb(255, 255, 255);'>or</h3>", unsafe_allow_html=True)
    paper_title = st.text_input("Enter research paper title", placeholder="Research paper title")
    
    # If a specific paper title is provided, retrieve that paper
    if st.button("Search"):
        if paper_title:
            encoded_paper_title = urllib.parse.quote(paper_title)
            url = f'http://export.arxiv.org/api/query?search_query={encoded_paper_title}&start=0&max_results=1'
            st.markdown(f"Obtained arXiv paper:")
        else:
            encoded_search_text = urllib.parse.quote(search_text)
            url = f'http://export.arxiv.org/api/query?search_query=all:{encoded_search_text}&start=0&max_results={max_results}'
            st.markdown(f"Top {max_results} results for research papers on {search_text[0:-3]} obtained from arxiv:")
        
        # components.html(modal_content, height=200, scrolling=True)
        data = urllib.request.urlopen(url)

        # Parse the data using feedparser
        parsed_data = feedparser.parse(data)
        
        i = 0
        # Accessing entries for each article
        for entry in parsed_data.entries:
            st.markdown(f"Title: {entry.title}")
            
            names = [person['name'] for person in entry.authors]
            all_authors_name = ', '.join(names)
            st.markdown(f"Authors: {all_authors_name}")
            st.markdown(f"Published: {entry.published}")
            st.markdown(f"Summary: {entry.summary}")
            st.markdown(f"Link: {entry.link}")
            st.button("Add", key = f"Add {i}")
            #### add functionality for adding the documents to the pdf embeddings
            st.markdown("--------------------------------------------------------")            
            i = i + 1

    if st.button("Process"):
       spinner_complete = st.empty()
       with st.spinner("Processing..."):
            # reading the pdf content 
            pdf_content = ""
            for uploaded_file in uploaded_files:
                pdf_reader = PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    pdf_content += page.extract_text()

            # splitting the pdf content
            splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 100) # this line is essentially splitting up the text into the described number of chunks
            text = splitter.split_text(pdf_content) # this is assigning the chunked documents into a list
            
            # creagting the vectorstores
            embeddings = OpenAIEmbeddings()
            # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
            vectorstore = FAISS.from_texts(texts=text, embedding=embeddings)

            llm = ChatOpenAI(model = "gpt-3.5-turbo", temperature = 0.0)
            # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})

            memory = ConversationBufferMemory(
                memory_key = 'chat_history', return_messages = True)
            
            st.session_state.conversation = ConversationalRetrievalChain.from_llm(
                llm = llm,
                retriever = vectorstore.as_retriever(),
                memory = memory
            )

            spinner_complete.markdown("<h3 style='font-size: 16px; color: rgb(255, 255, 255);'>Documents Processed!</h3>", unsafe_allow_html=True)
