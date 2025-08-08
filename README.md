# 🏏 IPL MCP Server - Natural Language Cricket Query System

## 📌 Project Overview

**IPL MCP Server** is a full-stack project developed as part of a Data Analyst Technical Assessment. The system ingests IPL match data (in JSON format), stores it in a relational MySQL database, and allows users to query this data using natural English via a REST API. The queries are interpreted and translated into SQL using **LLaMA 3 (via Ollama)** and **RapidFuzz** fuzzy matching. This server is designed to integrate seamlessly with **Claude Desktop**.

---

## 🧠 Key Features

* ✅ Parses and stores detailed IPL JSON match data into a normalized MySQL schema.
* 📟 Translates natural language questions to SQL using LLaMA 3.
* 🎯 Fallback to fuzzy matching with RapidFuzz for unmatched queries.
* 🌐 MCP Server built using Flask to handle incoming questions and return JSON results.
* 🔌 Seamless connection to Claude Desktop via REST API.
* 📊 Supports complex analytics like top players, scorecards, partnerships, and match stats.

---

## 📂 Directory Structure

```
.
├── sql_insert.ipynb              # Loads JSON IPL data into MySQL database
├── mcp_server_main.ipynb         # MCP Server code using Flask + LLaMA 3 + SQL mapping
├── mcp_server_main.py            # Converted script from the notebook to run the server
├── tables.sql                    # SQL file to create all tables
├── IPL/                       # Folder containing IPL match JSON files
└── README.md                     # This file
```

---

## ⚙️ Tech Stack

* **Language**: Python
* **Backend**: Flask
* **Database**: MySQL
* **LLM**: LLaMA 3 via [Ollama]
* **Query Matching**: RapidFuzz (fuzzy string matching)
* **Integration**: Claude Desktop

---

## 🏐 Setup Instructions

### 1. 🛠️ Clone the Repository

```bash
git clone https://github.com/yourusername/ipl-mcp-server.git
cd ipl-mcp-server
```

### 2. 🔧 Install Dependencies

Install required packages using pip:

```bash
pip install flask pandas rapidfuzz mysql-connector-python requests
```

### 3. 🧱 Create MySQL Database & Tables

* Ensure MySQL is running on your system.
* Create a database named `cric_data`.
* Use the `schema.sql` file to create all necessary tables.

```sql
CREATE DATABASE cric_data;
-- Run the SQL schema from tables.sql
```

### 4. 🏏 Load IPL Data

Edit the following fields in `sql_insert.ipynb`:

```python
host="127.0.0.1",
user="root",
password="your_mysql_password",
database="cric_data",
DATA_DIR = r"D:\Path\To\IPL_JSON"
```

Then run the notebook to insert data from all match JSON files into the database.

### 5. 🤖 Start LLaMA 3 via Ollama

Ensure [Ollama](https://ollama.com/) is installed, then run:

```bash
ollama run llama3
```

### 6. 🚀 Run the MCP Server

Convert the server notebook to a Python script:

```bash
jupyter nbconvert --to script "mcp_server_main.ipynb"
```

Then start the server:

```bash
python mcp_server_main.py
```

Server will run on: `http://127.0.0.1:5000`

### 7. 📡 Test via Curl or Claude Desktop

Example CURL command:

```bash
curl -X POST http://127.0.0.1:5000/query \
     -H "Content-Type: application/json" \
     -d "{\"question\": \"what was the highest total score\"}"
```
