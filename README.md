# Set up FastAPI backend and streamlit frontend for Agentic Ticket System


### Ollama (to run models locally)

These are the steps to work with granite models and Ollama:

- Download for [macOS and install CLI](https://ollama.com/download/mac)
- Pull the model: `ollama pull <model_name>` for instance `ollama pull granite3.1-dense:latest`
- Check if Ollama model is on your machine: `ollama list`
- OPTIONAL Try running: `ollama run granite3.1-dense:latest "Hello"`


### backend

Open backend in integrated terminal.

Initialize a new environment with `uv venv`
OR initialize with specific python version `uv venv .venv --python=/usr/bin/python3.12` or if you are using homebrew `uv venv .venv --python=/opt/homebrew/bin/python3.12`

Activate the virtual environment `source .venv/bin/activate`

Install from requirements.txt `uv pip install -r requirements.txt`

Go to root folder `cd ../`

Save `.env.sample` to `.env` and optionally add further ollama models and watsonx credentials

Run your app using uvicorn `uvicorn backend.main:app --reload`

If you want to add further packages go to `cd backend` run `uv pip install somepackage anotherpackage`

Then freeze current env to requirements.txt `uv pip freeze > requirements.txt`

Reactivate if you run into `ModuleNotFoundError` with `source .venv/bin/activate`

Install from requirements.txt `uv pip install -r requirements.txt`


### frontend

Open frontend in integrated terminal

Initialize a new environment with `uv venv`

Activate the virtual environment `source .venv/bin/activate`

Install from requirements.txt `uv pip install -r requirements.txt`

Start streamlit app `streamlit run streamlit_app.py` or `streamlit run streamlit_app_llm_only.py`

Start ticket dashboard `streamlit run streamlit_ticket_dashboard.py`


### Set up local Table Plus DB

Download Table Plus for Mac or other platforms [here](https://tableplus.com/)

In Table Plus click create a new connection and select SQLite

Give it a name like `ticketapi`

Click select file and select the ticket.db file in your backend folder

Click Test, then click Connect