"""
Run this ONCE to create the company documents.
These are the documents the RAG agent will search.
Command: python create_documents.py
"""
import os

DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")
os.makedirs(DOCS_DIR, exist_ok=True)

hr_policy = """TECHVISION INDIA — HR POLICY DOCUMENT
Version 3.2 | Effective: January 2026

=======================================================
SECTION 1: LEAVE POLICY
=======================================================

1.1 Annual Leave
All full-time employees are entitled to 21 days of paid annual leave per calendar year.
Leave must be applied for at least 3 working days in advance through the HR portal.
Unused leave can be carried forward up to a maximum of 10 days to the next year.
Leave encashment is available for up to 5 days at the end of each financial year.

1.2 Sick Leave
Employees are entitled to 12 days of paid sick leave per year.
Medical certificate is required for sick leave exceeding 3 consecutive days.
Sick leave cannot be carried forward to the next year.

1.3 Casual Leave
6 days of casual leave are provided per year.
Casual leave must be applied for at least 1 working day in advance except in emergencies.

1.4 Maternity and Paternity Leave
Female employees are entitled to 26 weeks of paid maternity leave.
Male employees are entitled to 15 days of paid paternity leave.

1.5 Public Holidays
TechVision follows 12 national and regional public holidays per year.

=======================================================
SECTION 2: WORKING HOURS
=======================================================

2.1 Standard Hours
Standard working hours are 9:00 AM to 6:00 PM, Monday to Friday.
This includes a 1-hour lunch break. Total working hours per week: 40 hours.

2.2 Flexible Working
Employees in Engineering and Marketing are eligible for flexible working.
Core hours that all flex employees must be available: 11:00 AM to 4:00 PM.
Work from home is permitted up to 2 days per week with manager approval.

2.3 Overtime
Overtime is paid at 1.5x the hourly rate for hours beyond 40 per week.
All overtime must be pre-approved by the department head.
Maximum overtime permitted is 10 hours per week.

=======================================================
SECTION 3: PERFORMANCE REVIEW
=======================================================

3.1 Review Cycle
Performance reviews are conducted twice a year — in June and December.

3.2 Rating Scale
5 — Outstanding: Consistently exceeds all expectations
4 — Exceeds Expectations: Regularly exceeds most expectations
3 — Meets Expectations: Consistently meets all expectations
2 — Needs Improvement: Partially meets expectations
1 — Unsatisfactory: Does not meet minimum expectations

3.3 Review Process
Step 1: Employee completes self-assessment by the 1st of review month
Step 2: Manager completes assessment by the 10th
Step 3: One-on-one review meeting between 10th and 20th
Step 4: Final rating submitted to HR by 25th

=======================================================
SECTION 4: BONUS AND COMPENSATION
=======================================================

4.1 Performance Bonus
Annual performance bonus is paid in January based on December review rating.
Rating 5 (Outstanding): Bonus of 20% of annual CTC
Rating 4 (Exceeds Expectations): Bonus of 15% of annual CTC
Rating 3 (Meets Expectations): Bonus of 10% of annual CTC
Rating 2 (Needs Improvement): No bonus
Rating 1 (Unsatisfactory): No bonus, Performance Improvement Plan initiated

4.2 Sales Incentive
Sales department employees receive additional quarterly incentives.
Q1 and Q2 targets: 5% commission on revenue above target
Q3 and Q4 targets: 7% commission on revenue above target
Maximum annual incentive is capped at 30% of annual CTC.

4.3 Salary Revision
Annual salary revision is effective from April 1st each year.
Rating 5: 15-20% increment
Rating 4: 10-15% increment
Rating 3: 5-10% increment
Rating 2: 0-5% increment
Rating 1: No increment

=======================================================
SECTION 5: GRIEVANCE POLICY
=======================================================

5.1 Reporting a Grievance
Employees can report grievances through the HR portal or directly to HR.
All grievances are acknowledged within 2 working days.
Investigation is completed within 15 working days.

5.2 Escalation
If unsatisfied with the outcome, employees can escalate to the HR Director.
Final escalation is to the CEO for unresolved matters.
"""

employee_handbook = """TECHVISION INDIA — EMPLOYEE HANDBOOK
Welcome to TechVision India | Updated: February 2026

=======================================================
CHAPTER 1: ABOUT TECHVISION INDIA
=======================================================

1.1 Company Overview
TechVision India is a technology training and AI solutions company founded in 2018.
We operate across 6 cities: Mumbai, Delhi, Bangalore, Chennai, Hyderabad, and Pune.
Our mission is to upskill India's technology workforce for the AI era.
We have trained over 50,000 professionals across 200+ enterprise clients.

1.2 Leadership Team
CEO: Rajiv Mehta (rajiv.mehta@techvision.in)
CTO: Priya Sharma (priya.sharma@techvision.in)
HR Director: Anita Gupta (anita.gupta@techvision.in)

=======================================================
CHAPTER 2: ONBOARDING
=======================================================

2.1 First Day Checklist
- Collect your access card from reception (Ground Floor, Block A)
- Meet your HR buddy assigned before joining
- Set up your laptop — IT support at extension 100
- Complete online onboarding modules on the Learning Portal
- Attend New Joiner Orientation at 10:00 AM in Conference Room B

2.2 Probation Period
All new employees serve a 3-month probation period.
Performance is reviewed at end of month 1 and month 3.
During probation, notice period is 2 weeks on either side.

2.3 Required Documents
Submit these to HR within first 3 days:
- Aadhar card (original + photocopy)
- PAN card
- Previous employer experience and relieving letter
- Last 3 months salary slips
- Bank account details for salary processing

=======================================================
CHAPTER 3: CODE OF CONDUCT
=======================================================

3.1 Professional Behaviour
Treat all colleagues, clients, and vendors with respect.
Discrimination of any kind is strictly prohibited and grounds for termination.
Sexual harassment complaints are handled under the POSH Act 2013.

3.2 Confidentiality
All company information and client data are confidential.
Confidentiality obligations continue for 2 years after leaving.

3.3 Conflict of Interest
Inform HR if you have a financial interest in a competitor or client.
Do not accept gifts worth more than Rs 1,000 from clients or vendors.
Moonlighting is not permitted.

=======================================================
CHAPTER 4: BENEFITS
=======================================================

4.1 Health Insurance
Group health insurance of Rs 5,00,000 per employee per year.
Coverage extends to spouse and up to 2 children.
Cashless treatment at 500+ network hospitals across India.

4.2 Learning and Development
Annual L&D budget of Rs 25,000 per employee.
Access to all internal TechVision courses free of charge.
Study leave of up to 5 days per year for approved certifications.

4.3 Employee Referral
Refer a candidate who gets hired and completes 3 months — receive Rs 15,000.
No limit on the number of referrals per employee.

=======================================================
CHAPTER 5: IMPORTANT CONTACTS
=======================================================

HR Helpdesk: hr@techvision.in | Extension 200
IT Support: it@techvision.in | Extension 100
Finance/Payroll: finance@techvision.in | Extension 300
"""

product_catalogue = """TECHVISION INDIA — PRODUCT CATALOGUE
Enterprise Solutions | 2026

=======================================================
SECTION 1: TRAINING COURSES
=======================================================

1.1 AI Course — Foundation to Advanced
Price: Rs 4,999 per participant
Duration: 40 hours (online, self-paced)
Current Stock/Seats Available: 150

Covers machine learning fundamentals, deep learning, neural networks.
Includes hands-on labs using Python, scikit-learn, TensorFlow, and PyTorch.
Certificate issued on completion, recognised by 200+ hiring companies.
Prerequisites: Basic Python knowledge

1.2 Cloud Workshop — AWS and Azure Fundamentals
Price: Rs 2,999 per participant
Duration: 16 hours (2 full days, instructor-led)
Current Stock/Seats Available: 200

Practical cloud computing covering both AWS and Azure.
Participants get hands-on access to live cloud environments.
Eligible for AWS Cloud Practitioner exam voucher discount.
Prerequisites: Basic understanding of servers and networking

1.3 GenAI Bootcamp — Building with Large Language Models
Price: Rs 8,999 per participant
Duration: 60 hours (6 weeks, blended)
Current Stock/Seats Available: 120

Covers the full GenAI stack — OpenAI, Claude, RAG, agents, MCP.
Each participant builds a capstone project deployed on AWS.
Placement assistance provided to all who complete the programme.
Prerequisites: Python proficiency, basic ML knowledge

=======================================================
SECTION 2: SOFTWARE PRODUCTS
=======================================================

2.1 ML Toolkit — Enterprise Machine Learning Platform
Price: Rs 9,999 per license per year
Current Stock/Licenses Available: 80

End-to-end ML platform for enterprise data teams.
No-code interface for data preprocessing, model training, and deployment.
Integrates with Snowflake, BigQuery, and Redshift.
SOC 2 Type II certified, GDPR compliant.
Minimum Contract: 5 licenses, 1 year

2.2 Data Dashboard — Business Intelligence and Analytics
Price: Rs 7,499 per license per year
Current Stock/Licenses Available: 60

Real-time business intelligence connecting to all major data sources.
Natural language query — ask questions in plain English and get charts.
100+ data source connectors, 50+ chart types.
Minimum Contract: 3 licenses, 1 year

=======================================================
SECTION 3: ENTERPRISE PACKAGES
=======================================================

3.1 Startup AI Package
Price: Rs 49,999 per year
Includes: 10 AI Course licences, 5 Cloud Workshop seats,
1 ML Toolkit licence, 8 hours of AI consulting

3.2 Enterprise AI Transformation Package
Price: Rs 2,49,999 per year
Includes: Unlimited AI Course and Cloud Workshop seats,
20 ML Toolkit licences, 10 Data Dashboard licences,
1 GenAI Bootcamp cohort (up to 20 participants),
40 hours of AI consulting, Dedicated Customer Success Manager

=======================================================
SECTION 4: CONTACT
=======================================================

Sales: sales@techvision.in | 1800-TECHVIS (toll free)
Demo Requests: demo@techvision.in
Payment: Bank transfer, Credit card, UPI, Purchase order
All prices exclusive of GST (18%).
"""

with open(os.path.join(DOCS_DIR, "hr_policy.txt"), "w") as f:
    f.write(hr_policy)
with open(os.path.join(DOCS_DIR, "employee_handbook.txt"), "w") as f:
    f.write(employee_handbook)
with open(os.path.join(DOCS_DIR, "product_catalogue.txt"), "w") as f:
    f.write(product_catalogue)

print("Documents created:")
for fname in os.listdir(DOCS_DIR):
    size = os.path.getsize(os.path.join(DOCS_DIR, fname))
    print(f"  {fname} ({size:,} bytes)")
