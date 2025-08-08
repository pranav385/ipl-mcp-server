#!/usr/bin/env python
# coding: utf-8

# In[1]:


# !pip install flask mysql-connector-python


# In[2]:


import mysql.connector
from flask import Flask, request, jsonify
from threading import Thread
import pandas as pd
from rapidfuzz import process
import time
import requests


# In[ ]:





# ### 🧠 Question Mapping Using Language Model API
# 
# This code defines a simple NLP-based assistant that maps a user's natural language question to a predefined list of known questions. 
# 
# - The `known_questions` list contains all supported queries the assistant can recognize.
# - The `prompt_builder(user_main_question)` function constructs a prompt string for the language model. It asks the model to match the user's input with the most relevant known question.
# - The `question_map(question)` function:
#   - Sends the constructed prompt to a locally hosted LLaMA3 language model via a REST API (`http://localhost:11434/api/generate`).
#   - Parses the response and returns the matched known question.
#   - If the model responds with `"None"`, or if an error occurs (e.g., timeout, server issue), it returns `None`.
# 
# This mechanism is useful for handling flexible user input by grounding it to a fixed set of query types that can be handled downstream.
# 

# In[4]:


import requests

known_questions = [
    "show me all matches in the dataset",
    "which team won the most matches",
    "what was the highest total score",
    "show matches played in mumbai",
    "who scored the most runs across all matches",
    "which bowler took the most wickets",
    "show me virat kohli's batting stats",
    "who has the best bowling figures in a single match",
    "what's the average first innings score",
    "which venue has the highest scoring matches",
    "show me all centuries scored",
    "what's the most successful chase target",
    "which team has the best powerplay performance",
    "show me the scorecard for match between CSK and MI",
    "how many sixes were hit in the final",
    "what was the winning margin in the closest match",
    "show partnerships over 100 runs"
]

def prompt_builder(user_main_question):
    options = "\n".join(f"- {q}" for q in known_questions)
    return f"""You are a helpful assistant.

Given the user's question below, match it to the most relevant known question from the list.

Only return the matched known question exactly as it appears. If there is no suitable match, return "None".
Only return question no extra text.

User Question:
{user_main_question}

Known Questions:
{options}
"""

def question_map(question):
    prompt = prompt_builder(question)
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=15
        )
        response.raise_for_status()
        mapped_question = response.json().get("response", "").strip()
        
        if mapped_question.lower() == "none":
            return None
            
        return mapped_question

    except Exception as e:
        print(f"❌ Error in question_map: {str(e)}")
        return None


# In[ ]:





# ### 🔎 Fuzzy Matching User Questions to Known Queries
# 
# This function `fuzzy_match_question` attempts to match a user's question to the most similar known question using fuzzy string matching.
# 

# In[6]:


def fuzzy_match_question(user_question, threshold=80):
    """
    Find the best fuzzy match for a user question from known questions
    
    Args:
        user_question (str): The user's input question
        threshold (int): Minimum similarity score to consider (0-100)
        
    Returns:
        str: The best matching known question or None
    """
    if not user_question or not user_question.strip():
        return None
        
    try:
        best_match, score, index = process.extractOne(
            user_question,
            known_questions,
            scorer=fuzz.token_set_ratio
        )
        
        print(f"🔍 Fuzzy match: '{user_question[:30]}' → '{best_match[:30]}' (Score: {score})")
        
        return best_match if score >= threshold else None
        
    except Exception as e:
        print(f"⚠️ Fuzzy matching error: {str(e)}")
        return None


# In[ ]:





# ### 🚀 Full Flask API for Translating Natural Language to SQL Queries
# 
# This block defines and launches a Flask-based API that processes user questions and returns data from a MySQL cricket database using SQL queries. Here's a breakdown of its components:
# 
# ---
# 
# #### ✅ **1. App Initialization**
# - `Flask(__name__)` creates the Flask application instance.
# - `db_config` stores the connection parameters for the MySQL database named `cric_data`.
# 
# ---
# 
# #### 🔁 **2. Question to SQL Mapping**
# - `map_question_to_sql(question)` checks whether the input question matches any known phrasing and returns the corresponding SQL query string.
# - Each `if-elif` block handles a specific known question and maps it to a custom SQL query.
# - If no match is found, it returns `None`.
# 
# ---
# 
# #### 🧠 **3. Question Resolution Logic (within `/query` endpoint)**
# - The `/query` endpoint accepts a POST request with a JSON body containing a natural language `"question"`.
# - The resolution flow:
#   1. **Direct Match:** Uses `map_question_to_sql()` to attempt a direct mapping.
#   2. **LLM Match:** If direct mapping fails, it calls `question_map()` (uses a local LLM API) to map the user question to a known phrasing, then reattempts SQL generation.
#   3. **Fuzzy Match:** If LLM mapping fails too, it uses `fuzzy_match_question()` to find the closest known question using fuzzy string matching.
#   4. If none of the above methods work, a 400 error is returned indicating the question wasn't understood.
# 
# ---
# 
# #### 🗄️ **4. SQL Execution**
# - Once an SQL query is generated, it connects to the MySQL database using `mysql.connector`, executes the query, fetches results, and returns them as a JSON response.
# - Errors in execution return a 500 response with the MySQL error message.
# 
# ---
# 
# #### 🧵 **5. Running the API in a Background Thread**
# - `run_flask()` starts the Flask app on port 5000.
# - It's run inside a Python `Thread` to avoid blocking the main execution (useful in environments like Jupyter notebooks).
# 
# ---
# 
# #### 🧩 **Overall Functionality**
# This code connects user input with structured database queries using a layered NLP + fuzzy logic system:
# - **Direct Mapping** ➜ **LLM Semantic Matching** ➜ **Fuzzy Matching**
# 
# It enables users to interact with complex cricket data using flexible natural language queries.
# 

# In[8]:


app = Flask(__name__)

db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "82107",
    "database": "cric_data",
    "ssl_disabled": True
}


def map_question_to_sql(question):
    question = question.lower().strip()

    if "show me all matches in the dataset" in question:
        return """
            SELECT 
                match_id,
                match_date,
                city,
                venue,
                team_1,
                team_2,
                toss_winner_team,
                toss_decision,
                winner_team,
                win_by_runs,
                win_by_wickets,
                player_of_match_id
            FROM 
                match_detail
            ORDER BY 
                match_date DESC
        """


    elif "which team won the most matches" in question:
        return """
            SELECT 
                winner_team, 
                COUNT(*) AS total_wins
            FROM 
                match_detail
            WHERE 
                winner_team IS NOT NULL
            GROUP BY 
                winner_team
            ORDER BY 
                total_wins DESC
            LIMIT 1
        """


    elif "what was the highest total score" in question:
        return """
            SELECT 
                match_id,
                inning_num,
                batting_team,
                SUM(runs_total) AS total_score
            FROM 
                deliveries
            GROUP BY 
                match_id, inning_num, batting_team
            ORDER BY 
                total_score DESC
            LIMIT 1
        """


    elif "show matches played in mumbai" in question:
        return """
            SELECT 
                match_id,
                match_date,
                team_1,
                team_2,
                venue
            FROM 
                match_detail
            WHERE 
                city = 'Mumbai'
            ORDER BY 
                match_date DESC
        """
    
    elif "who scored the most runs across all matches" in question:
        return """
            SELECT 
                p.player_name AS batsman,
                SUM(d.runs_batsman) AS total_runs
            FROM 
                deliveries d
            JOIN 
                players p ON d.batsman_id = p.player_id
            GROUP BY 
                p.player_name
            ORDER BY 
                total_runs DESC
            LIMIT 1
        """

    elif "which bowler took the most wickets" in question:
        return """
            SELECT 
                p.player_name AS bowler,
                COUNT(*) AS total_wickets
            FROM 
                wickets w
            JOIN 
                deliveries d ON w.delivery_id = d.delivery_id
            JOIN 
                players p ON d.bowler_id = p.player_id
            WHERE 
                w.dismissal_kind IN (
                    'bowled', 'caught', 'lbw', 'stumped', 'hit wicket', 'caught and bowled'
                )
            GROUP BY 
                p.player_name
            ORDER BY 
                total_wickets DESC
            LIMIT 1
        """

    elif "show me virat kohli's batting stats" in question:
        return """
            WITH player_match_stats AS (
                SELECT 
                    d.batsman_id,
                    p.player_name,
                    d.match_id,
                    COUNT(*) AS balls_faced,
                    SUM(d.runs_batsman) AS runs,
                    SUM(CASE WHEN d.runs_batsman = 4 THEN 1 ELSE 0 END) AS fours,
                    SUM(CASE WHEN d.runs_batsman = 6 THEN 1 ELSE 0 END) AS sixes
                FROM deliveries d
                JOIN players p ON d.batsman_id = p.player_id
                WHERE p.player_name = 'V Kohli'
                GROUP BY d.batsman_id, p.player_name, d.match_id
            ),
            dismissals AS (
                SELECT 
                    w.player_dismissed_id,
                    COUNT(DISTINCT d.match_id) AS times_out
                FROM wickets w
                JOIN deliveries d ON w.delivery_id = d.delivery_id
                WHERE w.player_dismissed_id IS NOT NULL
                GROUP BY w.player_dismissed_id
            )
            SELECT 
                pms.player_name,
                COUNT(pms.match_id) AS innings_played,
                SUM(pms.runs) AS total_runs,
                MAX(pms.runs) AS highest_score,
                SUM(pms.fours) AS total_fours,
                SUM(pms.sixes) AS total_sixes,
                SUM(pms.balls_faced) AS balls_faced,
                COALESCE(d.times_out, 0) AS times_dismissed,
                ROUND(SUM(pms.runs) / NULLIF(d.times_out, 0), 2) AS batting_average,
                ROUND((SUM(pms.runs) / NULLIF(SUM(pms.balls_faced), 0)) * 100, 2) AS strike_rate,
                SUM(CASE WHEN pms.runs BETWEEN 50 AND 99 THEN 1 ELSE 0 END) AS fifties,
                SUM(CASE WHEN pms.runs >= 100 THEN 1 ELSE 0 END) AS centuries
            FROM player_match_stats pms
            LEFT JOIN dismissals d ON pms.batsman_id = d.player_dismissed_id
            GROUP BY pms.player_name, d.times_out
        """

    elif "who has the best bowling figures in a single match" in question:
        return """
            WITH bowler_match_stats AS (
                SELECT 
                    d.match_id,
                    d.bowler_id,
                    p.player_name,
                    SUM(d.runs_total) AS runs_conceded,
                    COUNT(w.wicket_id) AS wickets_taken
                FROM deliveries d
                LEFT JOIN wickets w ON d.delivery_id = w.delivery_id
                JOIN players p ON d.bowler_id = p.player_id
                GROUP BY d.match_id, d.bowler_id, p.player_name
            )
            SELECT 
                match_id,
                player_name AS bowler,
                wickets_taken,
                runs_conceded
            FROM bowler_match_stats
            ORDER BY wickets_taken DESC, runs_conceded ASC
            LIMIT 1
        """

    elif "what's the average first innings score" in question:
        return """
            SELECT 
                ROUND(AVG(first_innings_score), 2) AS avg_first_innings_score
            FROM (
                SELECT 
                    match_id,
                    SUM(runs_total) AS first_innings_score
                FROM deliveries
                WHERE inning_num = 1
                GROUP BY match_id
            ) AS first_innings_scores
        """

    elif "which venue has the highest scoring matches" in question:
            return """
                SELECT 
                    md.venue,
                    ROUND(AVG(total_score), 2) AS avg_match_score
                FROM (
                    SELECT 
                        match_id,
                        SUM(runs_total) AS total_score
                    FROM deliveries
                    GROUP BY match_id
                ) AS scores
                JOIN match_detail md ON md.match_id = scores.match_id
                GROUP BY md.venue
                ORDER BY avg_match_score DESC
                LIMIT 1
            """

    elif "show me all centuries scored" in question:
        return """
            SELECT 
                p.player_name,
                d.match_id,
                mp.team_name,
                SUM(d.runs_batsman) AS runs_scored,
                COUNT(*) AS balls_faced
            FROM deliveries d
            JOIN players p ON d.batsman_id = p.player_id
            JOIN match_players mp ON mp.player_id = p.player_id AND mp.match_id = d.match_id
            GROUP BY d.match_id, d.batsman_id
            HAVING runs_scored >= 100
            ORDER BY runs_scored DESC
        """

    elif "what's the most successful chase target" in question:
        return """
            WITH first_innings_scores AS (
                SELECT
                    match_id,
                    batting_team AS first_innings_team,
                    SUM(runs_total) AS target_score
                FROM deliveries
                WHERE inning_num = 1
                GROUP BY match_id, batting_team
            ),
            match_winners AS (
                SELECT
                    match_id,
                    winner_team
                FROM match_detail
            )
            SELECT 
                f.match_id,
                f.first_innings_team AS team_set_target,
                f.target_score,
                m.winner_team AS chased_by_team
            FROM first_innings_scores f
            JOIN match_winners m ON f.match_id = m.match_id
            WHERE f.first_innings_team <> m.winner_team
            ORDER BY f.target_score DESC
            LIMIT 1
        """

    elif "show me the scorecard for match between CSK and MI" in question:
        return """
            SELECT 
                m.match_id,
                d.inning_num,
                p.player_name AS batsman,
                SUM(d.runs_batsman) AS runs,
                COUNT(*) AS balls_faced,
                SUM(CASE WHEN d.runs_batsman = 4 THEN 1 ELSE 0 END) AS fours,
                SUM(CASE WHEN d.runs_batsman = 6 THEN 1 ELSE 0 END) AS sixes
            FROM deliveries d
            JOIN players p ON d.batsman_id = p.player_id
            JOIN match_detail m ON d.match_id = m.match_id
            WHERE (m.team_1 = 'Chennai Super Kings' AND m.team_2 = 'Mumbai Indians')
               OR (m.team_1 = 'Mumbai Indians' AND m.team_2 = 'Chennai Super Kings')
            GROUP BY m.match_id, d.inning_num, d.batsman_id
            ORDER BY m.match_id, d.inning_num, runs DESC
        """

    elif "how many sixes were hit in the final" in question:
        return """
            SELECT COUNT(*) AS sixes_in_final
            FROM deliveries d
            JOIN match_detail m ON d.match_id = m.match_id
            WHERE m.stage = 'Final' AND d.runs_batsman = 6
        """

    elif "what was the winning margin in the closest match" in question:
        return """
            SELECT 
                match_id,
                team_1,
                team_2,
                winner_team,
                win_by_runs,
                win_by_wickets,
                CASE 
                    WHEN win_by_runs IS NOT NULL AND win_by_runs > 0 THEN win_by_runs
                    WHEN win_by_wickets IS NOT NULL AND win_by_wickets > 0 THEN win_by_wickets
                END AS margin
            FROM match_detail
            WHERE (win_by_runs > 0 OR win_by_wickets > 0)
            ORDER BY margin ASC
            LIMIT 1
        """

    elif "show partnerships over 100 runs" in question:
        return """
            SELECT 
                match_id,
                inning_num,
                striker.player_name AS batter_1,
                non_striker.player_name AS batter_2,
                SUM(runs_batsman) AS partnership_runs
            FROM deliveries d
            JOIN players striker ON d.batsman_id = striker.player_id
            JOIN players non_striker ON d.non_striker_id = non_striker.player_id
            GROUP BY match_id, inning_num, batsman_id, non_striker_id
            HAVING partnership_runs > 100
            ORDER BY partnership_runs DESC
        """

    elif "which team has the best powerplay performance" in question:
        return """
            SELECT 
                batting_team,
                ROUND(AVG(powerplay_runs), 2) AS avg_powerplay_score
            FROM (
                SELECT 
                    match_id,
                    batting_team,
                    SUM(runs_total) AS powerplay_runs
                FROM deliveries
                WHERE over_num BETWEEN 1 AND 6
                GROUP BY match_id, batting_team
            ) AS powerplay_scores
            GROUP BY batting_team
            ORDER BY avg_powerplay_score DESC
            LIMIT 1
        """


    else:
        return None


@app.route("/query", methods=["POST"])
def query():
    user_question = request.json.get("question")

    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    sql_query = map_question_to_sql(user_question)

    mapped_question = None
    if not sql_query:
        mapped_question = question_map(user_question)
        if mapped_question and mapped_question != "None":
            mapped_question = mapped_question.lower()
            sql_query = map_question_to_sql(mapped_question)
            
    if not sql_query:
        fuzzy_match_user = fuzzy_match_question(user_question)
        if fuzzy_match_user:
            sql_query = map_question_to_sql(fuzzy_match_user)
        
        if not sql_query and mapped_question:
            fuzzy_match_mapped = fuzzy_match_question(mapped_question)
            if fuzzy_match_mapped:
                sql_query = map_question_to_sql(fuzzy_match_mapped)

    if not sql_query:
        return jsonify({"error": "Sorry, I don't understand that question yet."}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql_query)
        result = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({"question": user_question, "result": result})

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500


from threading import Thread

def run_flask():
    app.run(debug=True, port=5000, use_reloader=False)

Thread(target=run_flask).start()



# In[ ]:





# In[9]:


import requests

response = requests.post(
    "http://127.0.0.1:5000/query",
    json={"question": "partnerships over 100"}
)


(response.json())


# In[ ]:




