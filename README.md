# AskCompany — Enterprise AI Assistant
### Capstone Project | Enterprise GenAI Course

---

## What Is This? hey hey hey

AskCompany is an AI assistant for a company called TechVision India.
Employees can ask questions in plain English and get accurate answers.

It knows about:
- Company HR policies, leave rules, bonuses, working hours (from documents)
- Employee records, salaries, departments, cities (from database)
- Product catalogue, pricing, features (from documents)
- Sales performance, revenue, top sellers (from database)

It also remembers the conversation — follow-up questions work naturally.
And you can upload new documents at any time — they become searchable immediately.

---

## Project Files — What Each File Does

```
askcompany/
│
├── setup_db.py          ← Creates company.db with employees, products, sales
├── create_documents.py  ← Creates 3 company text documents
│
├── rag_agent.py         ← Searches documents and answers document questions
├── db_agent.py          ← Queries the database and answers data questions
├── orchestrator.py      ← Decides which agent to use for each question
│
├── main.py              ← FastAPI — the HTTP API serving the whole system
├── frontend/
│   └── app.py           ← Streamlit — the chat interface users see
│
├── documents/           ← Company text documents (created by create_documents.py)
│   ├── hr_policy.txt
│   ├── employee_handbook.txt
│   └── product_catalogue.txt
│
├── vectorstore/         ← Saved embeddings index (auto-created by rag_agent.py)
│   └── index.json
│
├── company.db           ← SQLite database (created by setup_db.py)
├── requirements.txt     ← Python packages to install
└── .env                 ← Your OpenAI API key (you must fill this in)
```

---

## Architecture — How Everything Connects

```
User types a question in browser (localhost:8501)
                |
                | HTTP POST /ask  with question + conversation history
                v
        FastAPI (main.py) — port 8000
                |
                v
        Orchestrator (orchestrator.py)
        Reads the question, decides which agent to call:
            |                       |
            v                       v
    RAG Agent               Database Agent
    (rag_agent.py)          (db_agent.py)
    Searches documents      Queries SQLite directly
    using embeddings        using Python functions
            |                       |
            v                       v
    documents/*.txt         company.db
    (hr_policy,             (employees,
     handbook,               products,
     product_catalogue)      sales)
            |                       |
            └───────────┬───────────┘
                        v
                 OpenAI GPT-4o-mini
                 Generates the final
                 natural language answer
                        |
                        v
                Answer returned to FastAPI
                        |
                        v
                Streamlit shows it in chat
```

---

## The Three Agents Explained

### RAG Agent (rag_agent.py)
RAG = Retrieval Augmented Generation

The RAG agent handles questions about company policies and documents.
It does NOT just paste the whole document into OpenAI — that would be slow and expensive.

Instead it:
1. Breaks documents into 500-character chunks
2. Converts each chunk to a vector (list of numbers) using OpenAI embeddings
3. When a question comes in, converts the question to a vector
4. Finds the chunks with the most similar vectors (cosine similarity)
5. Sends only those relevant chunks to OpenAI with the question
6. Returns an answer grounded in the document — no hallucination

Example:
Q: "How many leave days do we get?"
RAG finds the leave policy chunk, sends it to GPT, gets back "21 days annual leave"

### Database Agent (db_agent.py)
The database agent handles questions about employee and sales data.

It does NOT use MCP (unlike the previous version). It queries SQLite directly.

It has 10 pre-built query functions:
- get_all_employees()
- get_department_stats()
- get_employees_by_department(department)
- get_employees_by_city(city)
- get_top_earners(limit)
- get_sales_performance()
- get_top_products(limit)
- get_all_products()
- get_company_overview()
- run_custom_sql(sql)  ← fallback for complex questions

When a question comes in:
1. GPT reads the list of functions and their descriptions
2. GPT picks the best function to call
3. The function runs and returns raw data
4. GPT formats the raw data into a natural language answer

Example:
Q: "Who are the top salespeople?"
GPT picks: get_sales_performance()
Function queries database, returns raw data
GPT formats: "Priya Patel leads with Rs 2,09,967 in revenue..."

### Orchestrator (orchestrator.py)
The orchestrator reads every question and decides:
- Is this about documents? → send to RAG agent
- Is this about data? → send to Database agent
- Does it need both? → call both, combine the answers

It uses conversation history to handle follow-up questions:
Q1: "Who are the top salespeople?"
Q2: "What city are they from?"  ← "they" refers to the salespeople from Q1

The orchestrator sends recent conversation history to GPT when classifying,
so GPT understands the context of follow-up questions.

---

## Conversation Memory — How It Works

Memory is stored in Streamlit's session state — a dictionary that persists
as long as the browser tab is open.

Every time you ask a question, Streamlit sends:
- The current question
- The full conversation history (all previous messages)

FastAPI passes this history to the orchestrator.
The orchestrator passes it to OpenAI.
OpenAI uses the history to understand context.

When you refresh the browser — memory resets. This is correct.
FastAPI is stateless — it does not store sessions. Only the browser does.

---

## Document Upload — How It Works

When you upload a document:
1. Streamlit sends the file bytes to FastAPI /upload endpoint
2. FastAPI saves the file to the documents/ folder
3. FastAPI calls reload_vectorstore()
4. RAG agent re-reads all documents including the new one
5. Creates new chunks and embeddings for the new document
6. Saves updated vectorstore to vectorstore/index.json
7. Returns success message

From that moment, questions about the new document get correct answers.
No restart required. No manual rebuild required.

The system auto-detects document changes using MD5 hashes.
If no documents changed since last run, it loads the existing vectorstore (fast).
If documents changed, it rebuilds (takes 1-2 minutes).

---

## Setup — Run in This Exact Order

### Step 1 — Install dependencies
Open Anaconda Prompt and run:
```
pip install -r requirements.txt
```

### Step 2 — Add your OpenAI API key
Open the .env file and replace the placeholder:
```
OPENAI_API_KEY=sk-proj-your-actual-key-here
```
No quotes. No spaces around the equals sign.

### Step 3 — Create the database
```
python setup_db.py
```
This creates company.db with 10 employees, 5 products, and 10 sales records.

### Step 4 — Create the company documents
```
python create_documents.py
```
This creates 3 text files in the documents/ folder:
- hr_policy.txt (leave, bonuses, working hours, performance reviews)
- employee_handbook.txt (onboarding, benefits, code of conduct)
- product_catalogue.txt (courses, software products, pricing)

### Step 5 — Build the RAG index
```
python rag_agent.py setup
```
This reads all documents, creates chunks, generates embeddings using OpenAI,
and saves the index to vectorstore/index.json.
This takes 1-2 minutes. Only needs to run once (or when documents change).

### Step 6 — Test each agent individually (optional but recommended)
```
python rag_agent.py
python db_agent.py
python orchestrator.py
```
Each prints test questions with answers.
If these work, the full system will work.

### Step 7 — Run the full system

Open TWO Anaconda Prompt windows.

Window 1 — Start FastAPI:
```
uvicorn main:app --port 8000 --reload
```
You should see: "Application startup complete" and "Vectorstore ready."

Window 2 — Start Streamlit:
```
streamlit run frontend/app.py
```
Browser opens automatically at http://localhost:8501

---

## Test Questions

### Document Questions (answer comes from text files)
- How many days of annual leave do employees get?
- What is the bonus percentage for Outstanding performance?
- What are the working hours at TechVision?
- What is the price of the GenAI Bootcamp?
- How do I report a grievance?
- What is the probation period for new employees?
- What is the health insurance coverage?

### Database Questions (answer comes from SQLite)
- Who are the top 3 salespeople by revenue?
- How many employees are in Engineering?
- What is the average salary in Marketing?
- Which product sold the most units?
- Show me all employees in Mumbai
- What is the total company revenue?
- Who is the highest paid employee?

### Combined Questions (needs both documents and database)
- What is the bonus policy and who qualifies for the highest bonus?
- What are the working hours and which Engineering employees work from Bangalore?
- What is the sales incentive and who earned the most from it?

### Memory Test (follow-up questions)
First ask: "Who are the top salespeople?"
Then ask: "What city are they based in?"
Then ask: "What is the sales incentive policy for them?"

Each follow-up should understand the context from the previous answer.

---

## Common Errors and Fixes

### "OPENAI_API_KEY not found" or 401 error
Fix: Check your .env file has the correct key. Make sure load_dotenv() is called.

### "No such table: employees"
Fix: Run python setup_db.py first.

### "vectorstore/index.json not found"
Fix: Run python rag_agent.py setup first.

### "streamlit is not recognized"
Fix: Make sure you are using Anaconda Prompt, not regular Command Prompt.

### FastAPI starts but Streamlit shows "API Offline"
Fix: Make sure FastAPI is fully started before checking. Look for "Application startup complete" in the FastAPI terminal.

### Document upload takes a long time
Normal: Rebuilding the vectorstore takes 1-2 minutes depending on document count.

### Answer seems wrong or unrelated
Check which source icon shows (📄 or 🗄️). If wrong source — the orchestrator misclassified.
Try rephrasing the question to be more specific about what you want.

---

## What This Project Demonstrates (For Portfolio)

| Skill | Where It Shows |
|-------|---------------|
| REST API development | FastAPI with proper endpoints |
| AI/LLM integration | OpenAI embeddings + GPT-4o-mini |
| RAG pipeline | Document chunking, embeddings, similarity search |
| Agent design | Database agent with function routing |
| Multi-agent orchestration | Orchestrator routing between agents |
| Conversation memory | History passed with every request |
| File handling | Document upload, save, delete |
| Frontend development | Streamlit chat interface |
| Software architecture | Clean separation of concerns across files |

---

## Next Steps (Classes 2-4)

Class 2: Containerise with Docker — one command starts everything
Class 3: Deploy to AWS EC2 — accessible from the internet
Class 4: Demo day — present your running system, portfolio discussion
