"""
============================================================
ORCHESTRATOR — orchestrator.py
============================================================

The brain of AskCompany. Routes every question to the right agent.

Three routes:
- "rag"      → answer is in documents (HR policy, handbook, products)
- "database" → answer needs database query (employees, sales, products data)
- "both"     → answer needs documents AND database

Includes conversation memory:
- Receives full conversation history with each question
- Uses history to understand follow-up questions
- "What is their salary?" after asking about salespeople works correctly

Run standalone:
    python orchestrator.py
============================================================
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from rag_agent import answer_from_documents, get_or_build_vectorstore
from db_agent import ask_database

load_dotenv(override=True)

client = OpenAI()

print("Loading document vectorstore...")
VECTORSTORE = get_or_build_vectorstore()
print("Vectorstore ready.")


def reload_vectorstore():
    """
    Called after a new document is uploaded.
    Forces rebuild so new document is immediately searchable.
    """
    global VECTORSTORE
    print("Reloading vectorstore with new documents...")
    VECTORSTORE = get_or_build_vectorstore()
    print("Vectorstore reloaded.")


def classify_question(question: str, conversation_history: list) -> str:
    """
    Classifies question as: rag, database, or both.
    Uses conversation history to handle follow-up questions.
    """
    history_text = ""
    if conversation_history:
        history_text = "\n\nRecent conversation:\n"
        for msg in conversation_history[-4:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"""You are a routing assistant for a company AI system.

The system has two knowledge sources:

1. DOCUMENTS: HR Policy (leave days, bonuses, performance reviews, working hours, grievances),
   Employee Handbook (onboarding, benefits, code of conduct, contacts, company overview),
   Product Catalogue (product descriptions, pricing, features, packages)

2. DATABASE: Employee records (names, departments, salaries, cities),
   Product sales data (revenue, units sold),
   Sales performance (which employee made which sales)
{history_text}
Classify this question:
- "rag"      → answer is in documents
- "database" → answer needs database query
- "both"     → needs both documents and database

Reply with ONLY one word: rag, database, or both

Question: {question}"""
        }]
    )
    classification = response.choices[0].message.content.strip().lower()
    if classification not in ["rag", "database", "both"]:
        classification = "rag"
    return classification


def ask(question: str, conversation_history: list = None) -> dict:
    """
    Main entry point for AskCompany.

    Takes a question and optional conversation history.
    Routes to the right agent.
    Returns answer with source information.
    """
    if conversation_history is None:
        conversation_history = []

    print(f"\nQuestion: {question}")
    print(f"History: {len(conversation_history)} messages")

    source = classify_question(question, conversation_history)
    print(f"Routing to: {source}")

    if source == "rag":
        # Enrich question with recent context for better retrieval
        enriched = question
        if conversation_history:
            recent = conversation_history[-2:]
            context = " ".join([m["content"] for m in recent])
            enriched = f"{context} {question}"

        result = answer_from_documents(enriched, VECTORSTORE)

        # If history exists, use it for a better answer
        if conversation_history and result["relevant"]:
            messages = conversation_history.copy()
            messages.append({
                "role": "user",
                "content": (
                    f"Based on this company document information:\n{result['answer']}\n\n"
                    f"Answer this question considering our conversation: {question}"
                )
            })
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500
            )
            final_answer = response.choices[0].message.content
        else:
            final_answer = result["answer"]

        return {
            "answer": final_answer,
            "source": "documents",
            "details": {"document_sources": result.get("sources", [])}
        }

    elif source == "database":
        # Include conversation history for follow-up understanding
        if conversation_history:
            history_context = "\n".join([
                f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
                for m in conversation_history[-4:]
            ])
            enriched = (
                f"Given this conversation:\n{history_context}\n\n"
                f"Answer: {question}"
            )
        else:
            enriched = question

        result = ask_database(enriched)
        return {
            "answer": result["answer"],
            "source": "database",
            "details": {"function_used": result.get("function_used", "")}
        }

    else:
        # Both — fetch from documents and database, then synthesise
        print("Fetching from both sources...")

        rag_result = answer_from_documents(question, VECTORSTORE)
        db_result = ask_database(question)

        messages = conversation_history.copy() if conversation_history else []
        messages.append({
            "role": "user",
            "content": (
                f"Question: {question}\n\n"
                f"From company documents:\n{rag_result['answer']}\n\n"
                f"From company database:\n{db_result['answer']}\n\n"
                f"Combine both into one clear, complete answer. "
                f"Do not say 'from documents' or 'from database' — just give a unified answer."
            )
        })

        synthesis = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=600
        )

        return {
            "answer": synthesis.choices[0].message.content,
            "source": "both",
            "details": {
                "document_sources": rag_result.get("sources", []),
                "function_used": db_result.get("function_used", "")
            }
        }


if __name__ == "__main__":
    print("Orchestrator Test")
    print("=" * 60)

    tests = [
        "How many days of annual leave do we get?",
        "Who are the top 3 salespeople by revenue?",
        "What is the bonus policy and who in Sales would qualify for the highest bonus?",
        "What is the price of the GenAI Bootcamp?",
        "How many engineers do we have and what is their average salary?",
    ]

    for q in tests:
        print(f"\nQ: {q}")
        result = ask(q)
        print(f"Source: {result['source']}")
        print(f"A: {result['answer']}")
        print("-" * 60)
