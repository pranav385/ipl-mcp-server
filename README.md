# 🏏 IPL MCP Server – Natural Language Cricket Query System

**Project Overview**  
IPL MCP Server is a full-stack project built as a Data Analyst technical assessment. It ingests IPL match JSON (from cricsheet.org), normalizes and stores it in a MySQL database, and exposes a Flask API that accepts natural-language cricket questions and returns precise JSON responses.

The question → SQL mapping uses a layered strategy:
1. Template-based direct mapping  
2. Semantic matching via LLaMA 3 (local LLM run with Ollama)  
3. Fuzzy matching fallback using RapidFuzz

Results are returned as JSON so clients (e.g., Claude Desktop) can easily consume them.

---

# 🧠 Key Features
- Parse IPL JSON into a normalized MySQL schema  
- Use LLaMA 3 for semantic question understanding (via Ollama)  
- RapidFuzz fuzzy matching fallback to improve coverage  
- Flask REST API that returns JSON responses  
- Designed to integrate with the Claude Desktop MCP protocol  
- Supports extensive cricket analytics: player stats, match details, venues, partnerships, powerplays, and more

---

# 📂 Project Structure
~~~
.
├── ipl_sql_insert.ipynb       # Notebook: Load IPL JSON into MySQL
├── ipl_mcp_server.ipynb       # Notebook: Flask MCP Server with LLaMA 3 & SQL mapping
├── ipl_mcp_server.py          # Python script: Server implementation
├── tables.sql                 # SQL schema for database & table creation
├── IPL_10/                    # Directory containing IPL JSON match files
└── README.md                  # This file
~~~

---

# ⚙️ Tech Stack

| Component            | Technology                         |
|---------------------:|------------------------------------|
| Programming Language | Python                             |
| Web Framework        | Flask                              |
| Database             | MySQL                              |
| Language Model       | LLaMA 3 (via Ollama)               |
| Fuzzy Matching       | RapidFuzz                          |
| Integration          | Claude Desktop                      |

---

# 🏐 Setup Instructions

## 1. Clone the repository
~~~
git clone https://github.com/pranav385/ipl-mcp-server.git
cd ipl-mcp-server
~~~

## 2. Install dependencies
~~~
pip install flask pandas rapidfuzz mysql-connector-python requests
~~~

## 3. Setup MySQL database
Ensure MySQL is running locally, then create the database and tables:
~~~
mysql -u root -p < tables.sql
~~~
Update DB credentials in the notebooks / scripts as needed.

## 4. Load IPL JSON data
- Configure the data path and DB credentials in `ipl_sql_insert.ipynb`.  
- Run the notebook to parse JSON files from `IPL_10/` and populate the DB.

## 5. Start LLaMA 3 model (via Ollama)
- Install Ollama: https://ollama.com/  
- Launch the model:
~~~
ollama pull llama3
ollama run llama3
~~~

## 6. Run the MCP Server
convert the notebook to a script:
~~~
jupyter nbconvert --to script "ipl_mcp_server.ipynb"
~~~
Run the server:
~~~
python ipl_mcp_server.py
~~~
The server listens on: `http://127.0.0.1:5000`

## 7. Test the server
Example 1 `curl` request:
~~~
curl -X POST http://127.0.0.1:5000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "what was the highest total score"}'
~~~

Response 
~~~
{
  "mapped_question": null,
  "question": "what was the highest total score",
  "result": [
    {
      "inning_num": 1,
      "match_id": "1473439",
      "team_name": "Sunrisers Hyderabad",
      "total_runs": "286"
    }
  ]
}

~~~

Example 2 `curl` request:
~~~
curl -X POST http://127.0.0.1:5000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "highest total score"}'
~~~

Response 
~~~
{
  "mapped_question": "what was the highest total score",
  "question": "highest total score",
  "result": [
    {
      "inning_num": 1,
      "match_id": "1473439",
      "team_name": "Sunrisers Hyderabad",
      "total_runs": "286"
    }
  ]
}

~~~

### Explanation of `mapped_question` field

- In the **first example**, the user’s question is `"what was the highest total score"`, which **exactly matches** one of the predefined template questions or intents in the MCP server’s mapping logic. Because it’s already a recognized, canonical question, the server sets `"mapped_question": null` to indicate no further mapping was needed.

- In the **second example**, the user asked `"highest total score"` — a shorter, less formal phrase. The server uses the LLaMA 3 model to find the **closest matching canonical question** it understands, which in this case is `"what was the highest total score"`. So the `"mapped_question"` field contains that canonical question, showing how LLaMA 3 interpreted and mapped the user’s input before querying the database.

In other words:

| `mapped_question` value | Meaning                                                |
|------------------------|--------------------------------------------------------|
| `null`                 | User’s question already matches a known canonical question — no mapping needed. |
| `<string>`             | The server (using LLaMA 3) mapped the user’s input to this canonical question before querying the database. |

---

# 🔍 Sample Supported Questions
- `show me all matches in the dataset`  
- `which team won the most matches`  
- `what was the highest total score`  
- `show matches played in Mumbai`  
- `who scored the most runs across all matches`  
- `which bowler took the most wickets`  
- `show me Virat Kohli's batting stats`  
- `who has the best bowling figures in a single match`  
- `what's the average first innings score`  
- `which venue has the highest scoring matches`  
- `show me all centuries scored`  
- `what's the most successful chase target`  
- `which team has the best powerplay performance`  
- `show me the scorecard for match between CSK and MI`  
- `how many sixes were hit in the final`  
- `what was the winning margin in the closest match`  
- `show partnerships over 100 runs`

---

# 📝 Notes & Tips
- Question processing priority: exact SQL templates → semantic LLM mapping → fuzzy matching fallback.  
- Make sure Ollama, LLaMA 3 are running before starting the server.  
- Extend `map_question_to_sql` to support additional question templates and edge cases.  

---

# 🗄️ Database Schema Overview

## Setup (example)
~~~
DROP DATABASE IF EXISTS ipl_data;
CREATE DATABASE ipl_data;
USE ipl_data;
~~~

## Core tables (high level)
- **teams** — team_id (PK), team_name (unique)  
- **players** — player_id (PK), player_name, substitute_flag  
- **players_team** — mapping player ↔ team ↔ season (composite PK)  
- **match_detail** — match metadata: team1_id, team2_id, venue_id, date, toss, winner, player_of_match  
- **officials** — official_id, official_name  
- **match_officials** — link officials to matches with role info  
- **deliveries** — ball-by-ball data: batsman, bowler, runs, extras, innings, over, ball, batting_team, bowling_team  
- **wickets** — wicket events with dismissed_player_id, kind, fielder_id, delivery_id  
- **reviews** — umpire reviews: decision, review_type, umpire_call, team_id  
- **replacements** — player replacements during matches with reason and timestamp  
- **match_players** — players participating in a match, team association  
- **powerplay** — powerplay phases per match (start_over, end_over, type)

## Constraints & Relationships
- Primary keys for uniqueness  
- Foreign keys to maintain referential integrity (e.g., `match_detail.team1_id → teams.team_id`)  
- Check constraints to validate data (positive overs, runs >= 0, valid wicket kinds)  
- Composite keys for many-to-many mapping tables (e.g., players ↔ teams ↔ seasons)
