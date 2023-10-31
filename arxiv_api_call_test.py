import urllib, urllib.request
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import BeautifulSoupTransformer
from langchain.chat_models import ChatOpenAI
from langchain.chains import create_extraction_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pprint
from langchain.text_splitter import MarkdownHeaderTextSplitter
import feedparser

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")

def extract(content: str, schema: dict):
    return create_extraction_chain(schema=schema, llm=llm).run(content)

schema = { #needed to only extract the required information from the webpage
    "properties": {
        "title": {"type": "string"},
        "paper_authors": {"type": "string"},
        "paper_summary": {"type": "string"},
        "number_of_citations": {"type": "string"},
    },
    "required": ["title", "paper_authors", "paper_summary", "number_of_citations"],
}

keyword = 'LLMs'
max_results = 3
url = f'http://export.arxiv.org/api/query?search_query=all:{keyword}&start=0&max_results={max_results}'
data = urllib.request.urlopen(url)

# Parse the data using feedparser
parsed_data = feedparser.parse(data)

print(f"Top {max_results} results for research papers on {keyword} obtained from arxiv:")
# Accessing entries for each article
for entry in parsed_data.entries:
    print("--------------------------------------------------------")
    print("Title:", entry.title)
    
    names = [person['name'] for person in entry.authors]
    all_authors_name = ', '.join(names)
    print("Authors:", all_authors_name)
    print("Published:", entry.published)
    print("Summary:", entry.summary)
    print("Link:", entry.link)
    
    # Retrieve the full-text content using the article link
    article_data = urllib.request.urlopen(entry.link)
    full_text = article_data.read().decode('utf-8')
    # print("Full Text:", full_text)  # This will be the HTML content of the article
    # print("------------------------------------------------------")

# print(data.read().decode('utf-8'))

# headers_to_split_on = [
#     ("<entry>", "Header 1"),
#     ("<title>", "Header 2"),
#     ("<summary>", "Header 3"),
#     ("<author>", "Header 4"),
# ]

# markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
# md_header_splits = markdown_splitter.split_text(data.read().decode('utf-8'))
# print(md_header_splits)

# splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000, 
#         chunk_overlap=0)
# splits = splitter.split_text(data.read().decode('utf-8'))
# print(splits)
# def llm_web_scraper(keyword, schema):
#     url = f'http://export.arxiv.org/api/query?search_query=all:{keyword}&start=0&max_results=10'
#     data = urllib.request.urlopen(url)
#     print("LLM extracted content:")

#         # Grab the first 1000 tokens of the site
#     splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
#         chunk_size=1000, 
#         chunk_overlap=0)
#     splits = splitter.split_documents(data.read().decode('utf-8'))
    
#     # Process the first split 
#     extracted_content = extract(
#         schema=schema, content=splits[0].page_content
#     )
#     pprint.pprint(extracted_content)
#     return extracted_content

# keyword = 'dropout'
# extracted_content = llm_web_scraper(keyword, schema=schema)

