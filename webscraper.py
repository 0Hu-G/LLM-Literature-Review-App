from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import BeautifulSoupTransformer
from langchain.chat_models import ChatOpenAI
from langchain.chains import create_extraction_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pprint

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")

def extract(content: str, schema: dict):
    return create_extraction_chain(schema=schema, llm=llm).run(content)

schema = { #needed to only extract the required information from the webpage
    "properties": {
        "stock_price_of_tsla": {"type": "string"},
        # "team_with_the_best_NRR": {"type": "string"},
    },
    "required": ["stock_price_of_tsla"],
}

def llm_web_scraper(urls, schema):
    # Load HTML
    loader = AsyncChromiumLoader(urls)
    html = loader.load()

    # Transform
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(html,tags_to_extract=["span"])
    print("LLM extracted content:")

        # Grab the first 1000 tokens of the site
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, 
        chunk_overlap=0)
    splits = splitter.split_documents(docs_transformed)
    
    # Process the first split 
    extracted_content = extract(
        schema=schema, content=splits[0].page_content
    )
    pprint.pprint(extracted_content)
    return extracted_content

urls = ["https://uk.finance.yahoo.com/?guccounter=1&guce_referrer=aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8&guce_referrer_sig=AQAAALaSfrrCmmvpj4JCgUB_gT3wzpmX-H75KiKMhEVFn2mQDnPHrNFc1XnH3i5JINGLH2JYeMvwqqkoa6g6zeAjGFd3DupgyA6K_JQkScFmqNQ7aa264VuXTVf8pgO8MSx0GD4mFa4lK3mcOvNg1mj4XAsJjREzhGujYpyYwNPuztYk"]
extracted_content = llm_web_scraper(urls, schema=schema)