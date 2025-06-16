# InWeb Info AI Assistant

A professional chatbot that uses GPT-4 and FAISS to provide intelligent responses about InWeb Info's services and offerings.

## Features

- 🌐 Automatic website scraping and content indexing
- 🔍 FAISS-powered semantic search for relevant context
- 🤖 GPT-4 integration for natural language understanding
- 💾 Persistent data storage to avoid repeated scraping
- 🎨 Clean and professional Streamlit UI
- 💬 Conversation history management

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd inwebinfo-assistant
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```
OPENAI_API_KEY=your_openai_api_key_here
BASE_URL=https://www.inwebinfo.com/
MAX_TOKENS=8192
MODEL_NAME=gpt-4
TEMPERATURE=0.7
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. On first run, the application will:
   - Scrape the InWeb Info website
   - Create FAISS embeddings
   - Build the search index

3. Once initialized, you can:
   - Ask questions about InWeb Info's services
   - Get detailed responses based on website content
   - Clear chat history as needed
   - Adjust response creativity using the temperature slider

## Project Structure

- `app.py`: Main Streamlit application
- `scraper.py`: Website scraping functionality
- `indexer.py`: FAISS indexing and search
- `chatbot.py`: GPT-4 integration and chat management
- `data/`: Directory for stored website data and FAISS index
- `requirements.txt`: Project dependencies

## Notes

- The scraping and indexing process runs only once
- Data is persistently stored for future sessions
- The chatbot uses context from the website to provide accurate responses
- Responses are generated using GPT-4 for high-quality interactions

## Demo Tips

1. Start with basic questions about InWeb Info's services
2. Explore specific technical solutions
3. Ask about company information and expertise
4. Test the context-awareness with follow-up questions 