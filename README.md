# LLM-Literature-Review-App
An LLM chatbot that scrapes the web for relevant articles and allows for QnA interaction with the PDFs for the user.

Features:

* First scrape the web for relevant papers relating to a scientific keyword
* Then store the PDFs as embeddings in a vector database
* Then allow for users to query from the different PDFs through an LLM
* Allows you to generate different summaries for the PDFs
* Allows you to generate an overall summary from all the PDFs 

Add your own `OPENAI_API_KEY` to the `.env` file for the code to work.

Main file to run: `pdf_reader_app.py`.

A langchgain tutorial notebook is included `LangChain.ipynb` to help users understand the underlying concepts of RAG. 
