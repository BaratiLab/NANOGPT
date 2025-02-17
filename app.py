import os
import time
import streamlit as st
from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
#from llama_index.readers.web import MainContentExtractorReader
from llama_index.core import SimpleDirectoryReader
from dotenv import load_dotenv
from elsapy.elsclient import ElsClient
#from elsapy.elsprofile import ElsAuthor, ElsAffil
from elsapy.elsdoc import FullDoc, AbsDoc
from elsapy.elssearch import ElsSearch
import json
#from llama_index.llms.groq import Groq
from llama_index.llms.openai import OpenAI
from get_acs_urls import scrape_and_extract_acs_urls, format_acs_query
from get_nature_urls import scrape_and_extract_nature_urls, format_nature_query
from save_acs_html import scrape_and_save_acs_html
from save_nature_html import scrape_and_save_nature_html
import shutil
from llama_index.core import StorageContext, load_index_from_storage
from elsevier_automation import elsapy
import requests

# Load environment variables from the .env file
load_dotenv()

# def elsapy(query, num_papers=5):
#     ## Load configuration
#     api_key = os.getenv('ELSEVIER_API_KEY')

#     if not api_key:
#         raise ValueError("API key is not set in environment variables.")

#     config = {
#         'apikey': api_key
#     }

#     ## Initialize client
#     client = ElsClient(config['apikey'])

#     def get_top_papers(query, num_papers=5):
#         # Initialize doc search object using ScienceDirect and execute search
#         doc_srch = ElsSearch(query, 'sciencedirect')
#         doc_srch.execute(client, get_all=False)
         
#         # Get top results based on the limit
#         top_results = doc_srch.results[:num_papers]
#         return top_results

#     def save_full_text(doc_list):
#         # Create directory for saving documents
#         save_dir = "/home/ach/Downloads/NANOGPT_DEMO/query_docs"
#         os.makedirs(save_dir, exist_ok=True)
        
#         for doc in doc_list:
#             # Initialize document with DOI or PII
#             if 'dc:identifier' in doc:
#                 identifier = doc['dc:identifier']
#                 if identifier.startswith('PII:'):
#                     pii = identifier.replace('PII:', '')
#                     full_doc = FullDoc(sd_pii=pii)
#                     filename = pii + '.json'
#                 elif identifier.startswith('DOI:'):
#                     doi = identifier.replace('DOI:', '')
#                     full_doc = FullDoc(doi=doi)
#                     filename = doi.replace('/', '_') + '.json'  # Replace '/' with '_' for valid filename
#                 else:
#                     print(f"Unknown identifier format: {identifier}")
#                     continue
#             else:
#                 print("Identifier not found in document.")
#                 continue
            
#             # Read the full documentCONDA
#             if full_doc.read(client):
#                 # Save the document locally
#                 filepath = os.path.join(save_dir, filename)
#                 with open(filepath, 'w') as outfile:
#                     json.dump(full_doc.data, outfile)
#                 print(f"Saved {full_doc.title} to {filepath}")
#             else:
#                 print(f"Failed to read document with identifier: {identifier}")

#     print(f"Searching for top {num_papers} papers for query: '{query}'")
#     top_papers = get_top_papers(query, num_papers)
#     print(f"Found {len(top_papers)} papers.")
#     save_full_text(top_papers)
#     st.session_state.data_loaded = True  # Flag to indicate data is loaded

######################### Models #########################
def load_llm():
    #os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    #llm = Groq(model="llama-3.2-90b-text-preview", max_tokens = 1024)
    #llm = OpenAI(model="gpt-4o-mini", temperature=0.3, max_tokens=512)
    llm = HuggingFaceInferenceAPI(
    model_name="meta-llama/Meta-Llama-3-8B-Instruct",
    temperature=0.3,
    max_tokens=512,
    num_output=512,
    token="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",  # Optional API token
    timeout=240,  # Set timeout to 60 seconds
    context_window=16000 # Optional context window size
)
    Settings.llm = llm
    return llm
    

def load_embeddings():
    """Load the embedding model."""
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-mpnet-base-v2")
    Settings.embed_model = embed_model
    


def load_index(prompt):

    elsapy(prompt)
    formatted_nature_query = format_nature_query(prompt)
    nature_url = f"https://www.springeropen.com/search?query={formatted_nature_query}&searchType=publisherSearch"
    print(nature_url)
    nature_urls = scrape_and_extract_nature_urls(nature_url)

    formatted_acs_query = format_acs_query(prompt)
    acs_url = f"https://pubs.acs.org/action/doSearch?field1=AllField&text1={formatted_acs_query}&field2=AllField&text2=&ConceptID=&ConceptID=&publication%5B%5D=ancac3&publication%5B%5D=aamick&publication%5B%5D=nalefd&publication=&openAccess=18&accessType=openAccess&Earliest="
    acs_urls = scrape_and_extract_acs_urls(acs_url)
    
    if len(acs_urls)>0:
        scrape_and_save_acs_html(acs_urls[0], "/home/ach/Downloads/NANOGPT_DEMO/query_docs")
 
    if len(nature_urls)>0:
        scrape_and_save_nature_html(nature_urls[0], "/home/ach/Downloads/NANOGPT_DEMO/query_docs")
    

    reader = SimpleDirectoryReader(input_dir="/home/ach/Downloads/NANOGPT_DEMO/query_docs")
    docs = reader.load_data()
    if st.session_state.count==0:
        for d in docs:
            st.session_state.index.insert(document = d)
        st.session_state.doc_list = [doc.metadata['file_name'] for doc in docs]

    st.session_state.count+=1

    if st.session_state.count!=0:
        new_doc_list = [doc.metadata['file_name'] for doc in docs]
        for d in docs:
            if d.metadata['file_name'] not in st.session_state.doc_list:
                st.session_state.index.insert(document=d)
    #vector_index = VectorStoreIndex.from_documents(docs)
    st.session_state.doc_list = new_doc_list
    return st.session_state.index
    

# Streamlit page configuration
st.set_page_config(
    page_title="NANOGPT",
    page_icon="🦙",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None
)
st.title("NANOGPT, powered by LlamaIndex 💬🦙")
st.info("Please hit the refresh button just once before prompting")

if 'count' not in st.session_state:
    st.session_state.count = 0


if "messages" not in st.session_state:
    # Load LLM and embeddings
    #st.session_state["additional_string"] = "Give me the answer to the last question followed by references for it"
    # if os.path.exists("/home/ach/Downloads/NANOGPT_DEMO/query_docs"):
    #     shutil.rmtree("/home/ach/Downloads/NANOGPT_DEMO/query_docs")  
    
    with st.spinner('"Loading the LLM, please wait..."'):
        time.sleep(3)
        st.session_state.llm = load_llm()
        load_embeddings()

    # rebuild storage context
    st.session_state.storage_context = StorageContext.from_defaults(persist_dir="/home/ach/Downloads/NANOGPT_DEMO/dummyindex_st") # paste the directory path of your ALREADY CREATED INDEX HERE

    # load index
    st.session_state.index = load_index_from_storage(st.session_state.storage_context)


    
        
# Initialize chat messages history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question!!!"}
    ]
    st.session_state.prompthis = []

    with st.chat_message(st.session_state.messages[0]["role"]):
        st.write(st.session_state.messages[0]["content"])


if st.sidebar.button("Refresh"):
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask me a questions?"}]
    if os.path.exists("/home/ach/Downloads/NANOGPT_DEMO/query_docs"):
        shutil.rmtree("/home/ach/Downloads/NANOGPT_DEMO/query_docs") 
    st.session_state.index = load_index_from_storage(st.session_state.storage_context)
    st.session_state.prompthis = [] 



# Prompt for user input and save to chat history
if prompt := st.chat_input("Your question"):
    with st.spinner("Thinking..."):          
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.prompthis.append(prompt)
        prompt_history = " ".join(st.session_state.prompthis)
        # Create vector store and index
        #vector_index = VectorStoreIndex.from_documents(documents)
        vector_index = load_index(prompt_history)
        st.session_state.query_engine  = vector_index.as_query_engine(similitary_top_k=3)

if "query_engine" in st.session_state.keys():  # Check if chat engine is initialized
    # Display the prior chat messages
    for message in st.session_state.messages[1:]:
        with st.chat_message(message["role"]):
            st.write(message["content"])



# # Generate a new response if the last message is not from the assistant 
# if st.session_state.messages[-1]["role"] != "assistant":     
#         with st.chat_message("assistant"):
#                 history = [msg["content"] for msg in st.session_state.messages]
#                 total_history = " ".join(history)
#                 #response = st.session_state.chat_engine.chat(st.session_state.messages[-1]["content"])
#                 response = st.session_state.query_engine.query(total_history)
#                 if response.response == "Empty Response":
#                     response = st.session_state.llm.complete(total_history)
#                     st.write(response.text)
#                     message = {"role": "assistant", "content": response.text}
#                 else:
#                     #file_names = "\n".join([info['file_name'].replace('.json', '').replace('_', '/') for info in response.metadata.values()])
#                     file_names = "\n".join([info['file_name'].replace('.json', '').replace('.txt', '').replace('_', '/') for info in response.metadata.values()])
#                     ans = response.response + file_names
#                     st.write(ans)
#                     message = {"role": "assistant", "content": ans}
#                 st.session_state.messages.append(message)

# # Generate a new response if the last message is not from the assistant
# if st.session_state.messages[-1]["role"] != "assistant":     
#     with st.chat_message("assistant"):
#         history = [msg["content"] for msg in st.session_state.messages]
#         total_history = " ".join(history)
#         # response = st.session_state.chat_engine.chat(st.session_state.messages[-1]["content"])
#         response = st.session_state.query_engine.query(total_history)
        
#         if response.response == "Empty Response":
#             response = st.session_state.llm.complete(total_history)
#             st.write(response.text)
#             message = {"role": "assistant", "content": response.text}
#         else:
#             # Extract DOIs from metadata
#             dois = [info['file_name'].replace('.json', '').replace('.txt', '').replace('_', '/') for info in response.metadata.values()]
#             ans = response.response

#             # Fetch reference details for each DOI
#             references = []
#             for doi in dois:
#                 doi = doi.strip()
#                 if doi:
#                     # Use CrossRef API to get reference details
#                     api_url = f"https://api.crossref.org/works/{doi}"
#                     try:
#                         r = requests.get(api_url)
#                         if r.status_code == 200:
#                             data = r.json()
#                             item = data['message']
#                             # Extract title and authors
#                             title = item.get('title', ['No title'])[0]
#                             authors = item.get('author', [])
#                             author_names = ', '.join([f"{a.get('given', '')} {a.get('family', '')}".strip() for a in authors])
#                             # Extract publication year
#                             year = item.get('issued', {}).get('date-parts', [[None]])[0][0]
#                             # Format the reference
#                             reference = f"{author_names} ({year}). {title}. DOI: {doi}"
#                             references.append(reference)
#                         else:
#                             references.append(f"Could not retrieve information for DOI: {doi}")
#                     except Exception as e:
#                         references.append(f"Error fetching DOI {doi}: {e}")
#             # Format references neatly
#             if references:
#                 ans += "\n\nReferences:\n" + "\n".join(references)
#             st.write(ans)
#             message = {"role": "assistant", "content": ans}
#         st.session_state.messages.append(message)



# Generate a new response if the last message is not from the assistant
if st.session_state.messages[-1]["role"] != "assistant":     
    with st.chat_message("assistant"):
        history = [msg["content"] for msg in st.session_state.messages]
        total_history = " ".join(history)
        # response = st.session_state.chat_engine.chat(st.session_state.messages[-1]["content"])
        response = st.session_state.query_engine.query(total_history)
        
        if response.response == "Empty Response":
            response = st.session_state.llm.complete(total_history)
            st.write(response.text)
            message = {"role": "assistant", "content": response.text}
        else:
            # Extract DOIs from metadata, remove duplicates, and preserve order
            dois = []
            seen = set()
            for info in response.metadata.values():
                doi = info['file_name'].replace('.json', '').replace('.txt', '').replace('_', '/').strip()
                if doi and doi not in seen:
                    seen.add(doi)
                    dois.append(doi)
            ans = response.response

            # Fetch reference details for each DOI
            references = []
            for doi in dois:
                # Use CrossRef API to get reference details
                api_url = f"https://api.crossref.org/works/{doi}"
                try:
                    r = requests.get(api_url)
                    if r.status_code == 200:
                        data = r.json()
                        item = data['message']
                        # Extract title and authors
                        title = item.get('title', ['No title'])[0]
                        authors = item.get('author', [])
                        author_names = ', '.join([f"{a.get('given', '')} {a.get('family', '')}".strip() for a in authors])
                        # Extract publication year
                        year = item.get('issued', {}).get('date-parts', [[None]])[0][0]
                        # Format the reference
                        reference = f"{author_names} ({year}). {title}. DOI: {doi}"
                        references.append(reference)
                    else:
                        references.append(f"Could not retrieve information for DOI: {doi}")
                except Exception as e:
                    references.append(f"Error fetching DOI {doi}: {e}")
            # Format references neatly with numbering and additional newlines
            if references:
                ans += "\n\n\nReferences:\n"
                for idx, ref in enumerate(references, start=1):
                    ans += f"\n[{idx}] {ref}\n"
            st.write(ans)
            message = {"role": "assistant", "content": ans}
        st.session_state.messages.append(message)
