"""
============================================================
DATABASE AGENT — db_agent.py
============================================================

This agent answers questions about company data stored in SQLite.

How it works:
1. Receives a question in plain English
2. Asks OpenAI which query function to call
3. Calls that function — which runs a SQL query directly
4. Sends the raw data + question back to OpenAI
5. Returns a natural language answer

No MCP. No protocol. Just Python functions that query SQLite.
This is the simplest, most direct approach.

Database tables:
- employees: id, name, department, salary, city
- products: id, name, category, price, stock
- sales: id, product_id, employee_id, quantity, sale_date, total_amount

Run standalone to test:
    python db_agent.py
============================================================
"""

import sqlite3
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI()
DB_PATH = os.path.join(os.path.dirname(__file__), "company.db")


# ============================================================
# DATABASE QUERY FUNCTIONS
# Each function does one specific query.
# These are called by the agent based on the question.
# ============================================================

def get_all_employees():
    """Returns all employees with name, department, salary and city."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, department, salary, city FROM employees ORDER BY name"
    )
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return "No employees found."
    lines = [f"{r[0]} | {r[1]} | Rs {r[2]:,} | {r[3]}" for r in rows]
    return "All Employees:\n" + "\n".join(lines)


def get_department_stats():
    """Returns salary statistics grouped by department."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT department, COUNT(*) as count,
               AVG(salary) as avg_sal,
               MIN(salary) as min_sal,
               MAX(salary) as max_sal
        FROM employees
        GROUP BY department
        ORDER BY avg_sal DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    lines = ["Department Statistics:"]
    for r in rows:
        lines.append(
            f"{r[0]}: {r[1]} employees | "
            f"Avg Rs {int(r[2]):,} | Min Rs {r[3]:,} | Max Rs {r[4]:,}"
        )
    return "\n".join(lines)


def get_employees_by_department(department: str):
    """Returns employees filtered by department name."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, salary, city FROM employees WHERE department = ? ORDER BY salary DESC",
        (department,)
    )
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return f"No employees found in {department} department."
    lines = [f"{r[0]} | Rs {r[1]:,} | {r[2]}" for r in rows]
    return f"Employees in {department}:\n" + "\n".join(lines)


def get_employees_by_city(city: str):
    """Returns employees filtered by city."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, department, salary FROM employees WHERE city = ? ORDER BY name",
        (city,)
    )
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return f"No employees found in {city}."
    lines = [f"{r[0]} | {r[1]} | Rs {r[2]:,}" for r in rows]
    return f"Employees in {city}:\n" + "\n".join(lines)


def get_top_earners(limit: int = 5):
    """Returns the highest paid employees."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, department, salary, city FROM employees ORDER BY salary DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    lines = [f"Top {limit} Highest Paid Employees:"]
    for i, r in enumerate(rows, 1):
        lines.append(f"{i}. {r[0]} ({r[1]}) — Rs {r[2]:,} — {r[3]}")
    return "\n".join(lines)


def get_sales_performance():
    """Returns total sales and revenue per employee."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.name, e.department,
               COUNT(s.id) as num_sales,
               SUM(s.total_amount) as total_revenue
        FROM sales s
        JOIN employees e ON s.employee_id = e.id
        GROUP BY e.id
        ORDER BY total_revenue DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    lines = ["Sales Performance by Employee:"]
    for r in rows:
        lines.append(
            f"{r[0]} ({r[1]}) | "
            f"Sales: {r[2]} | Revenue: Rs {int(r[3]):,}"
        )
    return "\n".join(lines)


def get_top_products(limit: int = 5):
    """Returns best selling products by revenue."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, p.category,
               SUM(s.quantity) as units_sold,
               SUM(s.total_amount) as revenue
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.id
        ORDER BY revenue DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    lines = [f"Top {limit} Products by Revenue:"]
    for i, r in enumerate(rows, 1):
        lines.append(
            f"{i}. {r[0]} ({r[1]}) | "
            f"Units: {r[2]} | Revenue: Rs {int(r[3]):,}"
        )
    return "\n".join(lines)


def get_all_products():
    """Returns all products with price and stock."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, category, price, stock FROM products ORDER BY name"
    )
    rows = cursor.fetchall()
    conn.close()
    lines = ["All Products:"]
    for r in rows:
        lines.append(
            f"{r[0]} ({r[1]}) | Rs {r[2]:,.0f} | Stock: {r[3]}"
        )
    return "\n".join(lines)


def get_company_overview():
    """Returns high-level company numbers."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM employees")
    emp = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM products")
    prod = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*), SUM(total_amount) FROM sales")
    s = cursor.fetchone()
    conn.close()
    return (
        f"TechVision India Overview:\n"
        f"Total employees: {emp}\n"
        f"Total products: {prod}\n"
        f"Total sales transactions: {s[0]}\n"
        f"Total revenue: Rs {int(s[1] or 0):,}"
    )


def run_custom_sql(sql: str):
    """
    Runs any SELECT query.
    Used as a fallback when no specific function covers the question.
    Only SELECT queries are allowed for security.
    """
    if not sql.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        conn.close()
        if not rows:
            return "Query returned no results."
        lines = [" | ".join(cols), "-" * 50]
        for row in rows:
            lines.append(" | ".join(str(v) for v in row))
        return "\n".join(lines)
    except Exception as e:
        return f"Query error: {str(e)}"


# ============================================================
# AVAILABLE FUNCTIONS — registered for routing
# ============================================================

AVAILABLE_FUNCTIONS = {
    "get_all_employees": {
        "fn": get_all_employees,
        "description": "Returns all employees. Use for general employee listing.",
        "args": []
    },
    "get_department_stats": {
        "fn": get_department_stats,
        "description": "Returns count, avg, min, max salary per department. Use for department comparisons.",
        "args": []
    },
    "get_employees_by_department": {
        "fn": get_employees_by_department,
        "description": "Returns employees in a specific department. Args: department (Engineering/Sales/Marketing/HR).",
        "args": ["department"]
    },
    "get_employees_by_city": {
        "fn": get_employees_by_city,
        "description": "Returns employees in a specific city. Args: city (Mumbai/Delhi/Bangalore/Chennai/Hyderabad/Pune).",
        "args": ["city"]
    },
    "get_top_earners": {
        "fn": get_top_earners,
        "description": "Returns highest paid employees. Args: limit (default 5).",
        "args": ["limit"]
    },
    "get_sales_performance": {
        "fn": get_sales_performance,
        "description": "Returns sales count and revenue per employee. Use for sales rankings and performance.",
        "args": []
    },
    "get_top_products": {
        "fn": get_top_products,
        "description": "Returns best selling products by revenue. Args: limit (default 5).",
        "args": []
    },
    "get_all_products": {
        "fn": get_all_products,
        "description": "Returns all products with price and stock levels.",
        "args": []
    },
    "get_company_overview": {
        "fn": get_company_overview,
        "description": "Returns total employees, products, sales count and revenue. Use for general company overview.",
        "args": []
    },
    "run_custom_sql": {
        "fn": run_custom_sql,
        "description": "Runs a custom SELECT query. Use for complex questions not covered by other functions.",
        "args": ["sql"]
    },
}


# ============================================================
# AGENT — routes question to right function
# ============================================================

def ask_database(question: str) -> dict:
    """
    Main function. Takes a plain English question.
    Routes to the right database function.
    Returns natural language answer.

    Steps:
    1. Build a list of available functions with descriptions
    2. Ask GPT which function to call
    3. If args needed, ask GPT to generate them
    4. Call the function
    5. Ask GPT to answer naturally based on the data
    """

    # Step 1: Build function list for routing
    function_list = "\n".join([
        f"- {name}: {info['description']}"
        for name, info in AVAILABLE_FUNCTIONS.items()
    ])

    # Step 2: Ask GPT which function to call
    routing_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": (
                f"Available database functions:\n{function_list}\n\n"
                f"Question: {question}\n\n"
                f"Which single function name should be called?\n"
                f"Reply with ONLY the function name."
            )
        }]
    )
    function_name = routing_response.choices[0].message.content.strip()

    # Fallback if GPT returns unknown function
    if function_name not in AVAILABLE_FUNCTIONS:
        function_name = "run_custom_sql"

    function_info = AVAILABLE_FUNCTIONS[function_name]

    # Step 3: Generate arguments if needed
    kwargs = {}
    if function_info["args"] and function_name != "run_custom_sql":
        for arg in function_info["args"]:
            arg_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": (
                        f"Question: {question}\n\n"
                        f"What value should the argument '{arg}' be?\n"
                        f"Reply with ONLY the value, nothing else."
                    )
                }]
            )
            value = arg_response.choices[0].message.content.strip()
            try:
                kwargs[arg] = int(value)
            except ValueError:
                kwargs[arg] = value

    elif function_name == "run_custom_sql":
        sql_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": (
                    f"Write a SQL SELECT query to answer: {question}\n"
                    f"Tables:\n"
                    f"  employees(id, name, department, salary, city)\n"
                    f"  products(id, name, category, price, stock)\n"
                    f"  sales(id, product_id, employee_id, quantity, sale_date, total_amount)\n"
                    f"Return ONLY the SQL query."
                )
            }]
        )
        kwargs["sql"] = sql_response.choices[0].message.content.strip()

    # Step 4: Call the function
    raw_data = function_info["fn"](**kwargs)

    # Step 5: Generate natural language answer
    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": (
                f"Question: {question}\n\n"
                f"Data from company database:\n{raw_data}\n\n"
                f"Give a clear, helpful answer based on this data."
            )
        }]
    )

    return {
        "answer": final_response.choices[0].message.content,
        "function_used": function_name,
        "raw_data": raw_data
    }


if __name__ == "__main__":
    print("Database Agent Test")
    print("=" * 50)

    test_questions = [
        "Who are the top 3 highest paid employees?",
        "Which product generated the most revenue?",
        "How many employees are in Engineering?",
        "What is the total company revenue from all sales?",
        "Show me all employees in Mumbai",
    ]

    for q in test_questions:
        print(f"\nQ: {q}")
        result = ask_database(q)
        print(f"Function: {result['function_used']}")
        print(f"A: {result['answer']}")
        print("-" * 40)
