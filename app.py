import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import httpx
from scraper import WebScraper
from indexer import FAISSIndexer
from chatbot import Chatbot

# Load environment variables
load_dotenv()

# Configure custom HTTP client
http_client = httpx.Client()

# Configure OpenAI with custom client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=http_client
)

# Streamlit page config
st.set_page_config(
    page_title="InWeb Info AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #f0f2f6;
    }
    .assistant-message {
        background-color: #e8f0fe;
    }
    .message-content {
        margin-top: 0.5rem;
    }
    .sidebar-content {
        padding: 1.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = Chatbot(
            model_name=os.getenv("MODEL_NAME", "gpt-4"),
            temperature=float(os.getenv("TEMPERATURE", 0.7))
        )
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'indexer' not in st.session_state:
        st.session_state.indexer = FAISSIndexer()

def setup_sidebar():
    """Setup sidebar with controls and information."""
    with st.sidebar:
        st.markdown("### Controls")
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.session_state.chatbot.clear_history()
            st.rerun()

def initialize_data():
    """Initialize website data and FAISS index."""
    if not os.path.exists("data/scraped_data.json"):
        with st.spinner("First-time setup: Scraping website content..."):
            scraper = WebScraper(os.getenv("BASE_URL", "https://www.inwebinfo.com"))
            scraped_data = scraper.scrape_website()
            
        with st.spinner("Building search index..."):
            st.session_state.indexer.build_index(scraped_data)
    
    if not os.path.exists("data/faiss_index.pkl"):
        with st.spinner("Building search index..."):
            scraper = WebScraper(os.getenv("BASE_URL", "https://www.inwebinfo.com"))
            scraped_data = scraper.scrape_website()
            st.session_state.indexer.build_index(scraped_data)

def main():
    # Initialize session state
    initialize_session_state()
    
    # Setup sidebar
    setup_sidebar()
    
    # Main content
    st.title("InWeb Info AI Assistant 🤖")
    st.markdown("""
    Welcome! I'm your AI assistant for InWeb Info. I can help you with:
    - Information about our services and solutions
    - Technical expertise and capabilities
    - Company details and experience
    - Project inquiries and consultations
    """)
    
    # Initialize data if needed
    initialize_data()
    
    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about InWeb Info..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get context from FAISS
        with st.spinner("Searching relevant information..."):
            context_chunks = st.session_state.indexer.search(prompt, k=3)
        
        # Get chatbot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.get_response(prompt, context_chunks)
                st.markdown(response)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main() 