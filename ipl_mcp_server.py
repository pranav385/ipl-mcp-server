#!/usr/bin/env python
# coding: utf-8

# In[1]:


# !pip install flask mysql-connector-python


# In[2]:


import mysql.connector
from flask import Flask, request, jsonify
from threading import Thread
import pandas as pd
from rapidfuzz import process, fuzz
import time
import requests
import logging


# In[ ]:





# In[3]:


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


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

# In[5]:


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
            logging.info("LLM returned 'None' for mapping question")
            return None
            
        logging.info(f"LLM mapped question to: {mapped_question}")
        return mapped_question

    except Exception as e:
        logging.error(f"❌ Error in question_map: {str(e)}")
        return None


# In[ ]:





# ### 🔎 Fuzzy Matching User Questions to Known Queries
# 
# This function `fuzzy_match_question` attempts to match a user's question to the most similar known question using fuzzy string matching.
# 

# In[7]:


def fuzzy_match_question(user_question, threshold=80):
    if not user_question or not user_question.strip():
        return None
        
    try:
        best_match, score, index = process.extractOne(
            user_question,
            known_questions,
            scorer=fuzz.token_set_ratio
        )
        logging.info(f"🔍 Fuzzy match: '{user_question[:30]}' → '{best_match[:30]}' (Score: {score})")
        return best_match if score >= threshold else None
        
    except Exception as e:
        logging.error(f"⚠️ Fuzzy matching error: {str(e)}")
        return None


# In[ ]:





# # 🚀 Full Flask API for Translating Natural Language to SQL Queries
# 
# This script implements a Flask API that accepts natural language questions, maps them to SQL queries for a MySQL cricket database (`cric_data`), executes those queries, and returns JSON results.
# 
# ---
# 
# ## ✅ 1. App Initialization
# - Creates a Flask app instance via `Flask(__name__)`.
# - Defines `db_config` with parameters for connecting to the MySQL `cric_data` database.
# 
# ---
# 
# ## 🔁 2. Question to SQL Mapping (`map_question_to_sql`)
# - Maps user questions (in lowercase) to predefined SQL queries.
# - Contains explicit mappings for known questions, returning SQL strings tailored for each.
# - Returns `None` if no exact mapping is found.
# 
# ---
# 
# ## 🧠 3. Question Resolution Logic (inside `/query` POST endpoint)
# - Receives a JSON POST with a `"question"` key.
# - The logic proceeds in this order:
#   1. **Direct Mapping:** Try to map the exact user question via `map_question_to_sql`.
#   2. **LLM-Based Mapping:** If no direct SQL found, sends the user question to a local LLM API (`question_map()`) which attempts to find the closest known question phrasing, then tries SQL mapping again.
#   3. **Fuzzy Matching:** If the LLM returns no match, attempts a fuzzy string match (`fuzzy_match_question()`) against known questions for approximate matching.
#   4. If no SQL query is found after all steps, returns HTTP 400 with an error message.
# 
# ---
# 
# ## 🗄️ 4. SQL Execution
# - Connects to MySQL using `mysql.connector` with `db_config`.
# - Executes the generated SQL query and fetches results as dictionaries.
# - Closes the database connection cleanly.
# - Returns a JSON response containing:
#   - The original user question.
#   - The SQL query used (for debugging/clarity).
#   - The query results.
# - If SQL execution fails, returns HTTP 500 with the error message.
# 
# ---
# 
# ## 🧵 5. Running the Flask API
# - Defines a `run_flask()` function that starts the Flask server on port 5000 with debugging enabled.
# - Runs this function inside a background thread (`Thread(target=run_flask).start()`), so the server runs asynchronously (useful for running inside Jupyter or other environments without blocking).
# 
# ---
# 
# ## 🧩 Overall Workflow
# - The API transforms flexible natural language questions into structured SQL commands by layering:
#   - Direct keyword matching
#   - Semantic LLM mapping
#   - Fuzzy string matching
# - This layered approach allows users to ask cricket-related questions in natural language and get accurate database responses.
# ata using flexible natural language queries.
# 

# In[9]:


app = Flask(__name__)

db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "your_password",
    "database": "ipl_data",
    "ssl_disabled": True
}


def map_question_to_sql(question):
    question = question.lower().strip()

    if "show me all matches in the dataset" in question:
        return """
            SELECT 
            md.match_id, 
            md.match_date, 
            md.city, 
            md.venue, 
            md.match_number, 
            md.season, 
            md.match_type,
            t1.team_name AS team1,
            t2.team_name AS team2
        FROM match_detail md
        JOIN teams t1 ON md.team1_id = t1.team_id
        JOIN teams t2 ON md.team2_id = t2.team_id
        ORDER BY md.match_date;
        """


    elif "which team won the most matches" in question:
        return """
            SELECT t.team_name, COUNT(*) AS wins
            FROM match_detail md
            JOIN teams t ON md.winner_team_id = t.team_id
            GROUP BY md.winner_team_id
            ORDER BY wins DESC
            LIMIT 1;
        """


    elif "what was the highest total score" in question:
        return """
            SELECT 
            d.match_id, 
            d.inning_num, 
            t.team_name,
            SUM(d.runs_total) AS total_runs
        FROM deliveries d
        JOIN teams t ON d.batting_team_id = t.team_id
        GROUP BY d.match_id, d.inning_num, t.team_name
        ORDER BY total_runs DESC
        LIMIT 1;
        """


    elif "show matches played in mumbai" in question:
        return """
            SELECT 
            md.match_id,
            md.match_date,
            md.venue,
            t1.team_name AS team1,
            t2.team_name AS team2
        FROM match_detail md
        JOIN teams t1 ON md.team1_id = t1.team_id
        JOIN teams t2 ON md.team2_id = t2.team_id
        WHERE md.city = 'Mumbai';
        """
    
    elif "who scored the most runs across all matches" in question:
        return """
            SELECT 
            p.player_name, 
            SUM(d.runs_batsman) AS total_runs
        FROM deliveries d
        JOIN players p ON d.batsman_id = p.player_id
        GROUP BY d.batsman_id
        ORDER BY total_runs DESC
        LIMIT 1;
        """

    elif "which bowler took the most wickets" in question:
        return """
            SELECT 
            p.player_name AS bowler_name,
            COUNT(w.wicket_id) AS wickets_taken
        FROM wickets w
        JOIN deliveries d ON w.delivery_id = d.delivery_id
        JOIN players p ON d.bowler_id = p.player_id
        WHERE w.dismissal_kind IN (
            'bowled', 'caught', 'lbw', 'stumped', 'hit wicket', 'caught and bowled'
        )
        GROUP BY d.bowler_id
        ORDER BY wickets_taken DESC
        LIMIT 1;
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
            WHERE p.player_name = 'Virat Kohli'
            GROUP BY d.batsman_id, p.player_name, d.match_id
        ),
        dismissals AS (
            SELECT 
                w.player_dismissed_id,
                COUNT(*) AS times_out
            FROM wickets w
            JOIN deliveries d ON w.delivery_id = d.delivery_id
            WHERE w.player_dismissed_id IS NOT NULL
            GROUP BY w.player_dismissed_id
        )
        SELECT 
            pms.player_name,
            COUNT(DISTINCT pms.match_id) AS innings_played,
            SUM(pms.runs) AS total_runs,
            MAX(pms.runs) AS highest_score,
            SUM(pms.fours) AS total_fours,
            SUM(pms.sixes) AS total_sixes,
            SUM(pms.balls_faced) AS balls_faced,
            COALESCE(d.times_out, 0) AS times_dismissed,
            ROUND(
                CASE WHEN d.times_out = 0 THEN NULL ELSE SUM(pms.runs) / d.times_out END
            , 2) AS batting_average,
            ROUND(
                CASE WHEN SUM(pms.balls_faced) = 0 THEN NULL ELSE (SUM(pms.runs) / SUM(pms.balls_faced)) * 100 END
            , 2) AS strike_rate,
            SUM(CASE WHEN pms.runs BETWEEN 50 AND 99 THEN 1 ELSE 0 END) AS fifties,
            SUM(CASE WHEN pms.runs >= 100 THEN 1 ELSE 0 END) AS centuries
        FROM player_match_stats pms
        LEFT JOIN dismissals d ON pms.batsman_id = d.player_dismissed_id
        GROUP BY pms.player_name, d.times_out;
        """

    elif "who has the best bowling figures in a single match" in question:
        return """
            WITH bowler_match_stats AS (
            SELECT
                d.bowler_id,
                p.player_name,
                d.match_id,
                COUNT(CASE 
                    WHEN w.wicket_id IS NOT NULL 
                         AND w.dismissal_kind IN ('bowled', 'caught', 'lbw', 'stumped', 'hit wicket', 'caught and bowled')
                    THEN 1
                    ELSE NULL
                END) AS wickets_taken,
                SUM(d.runs_batsman + d.runs_extras) AS runs_conceded
            FROM deliveries d
            LEFT JOIN wickets w ON d.delivery_id = w.delivery_id
            JOIN players p ON d.bowler_id = p.player_id
            GROUP BY d.bowler_id, p.player_name, d.match_id
        )
        SELECT
            player_name,
            match_id,
            wickets_taken,
            runs_conceded
        FROM bowler_match_stats
        ORDER BY wickets_taken DESC, runs_conceded ASC
        LIMIT 1;
        """

    elif "what's the average first innings score" in question:
        return """
            SELECT 
            ROUND(AVG(first_innings_total), 2) AS average_first_innings_score
            FROM (
                SELECT 
                    match_id,
                    SUM(runs_total) AS first_innings_total
                FROM deliveries
                WHERE inning_num = 1
                GROUP BY match_id
            ) AS first_innings_scores;
        """

    elif "which venue has the highest scoring matches" in question:
            return """
                SELECT 
                    md.venue,
                    ROUND(AVG(total_runs), 2) AS avg_total_runs
                FROM (
                    SELECT 
                        match_id,
                        SUM(runs_total) AS total_runs
                    FROM deliveries
                    GROUP BY match_id
                ) AS match_totals
                JOIN match_detail md ON match_totals.match_id = md.match_id
                GROUP BY md.venue
                ORDER BY avg_total_runs DESC
                LIMIT 5;
            """

    elif "show me all centuries scored" in question:
        return """
            WITH player_match_stats AS (
                SELECT 
                    d.batsman_id,
                    p.player_name,
                    d.match_id,
                    SUM(d.runs_batsman) AS runs_scored,
                    COUNT(*) AS balls_faced,
                    SUM(CASE WHEN d.runs_batsman = 4 THEN 1 ELSE 0 END) AS fours,
                    SUM(CASE WHEN d.runs_batsman = 6 THEN 1 ELSE 0 END) AS sixes
                FROM deliveries d
                JOIN players p ON d.batsman_id = p.player_id
                GROUP BY d.batsman_id, p.player_name, d.match_id
            )
            SELECT 
                player_name,
                match_id,
                runs_scored,
                balls_faced,
                fours,
                sixes
            FROM player_match_stats
            WHERE runs_scored >= 100
            ORDER BY runs_scored DESC, player_name, match_id;
        """

    elif "what's the most successful chase target" in question:
        return """
            SELECT 
            md.match_id,
            md.match_date,
            t.team_name AS chasing_team,
            md.win_by_wickets AS wickets_left,
            (SELECT SUM(d.runs_total) 
             FROM deliveries d 
             WHERE d.match_id = md.match_id AND d.batting_team_id = md.winner_team_id) AS chased_runs
        FROM match_detail md
        JOIN teams t ON md.winner_team_id = t.team_id
        WHERE md.win_by_wickets > 0
        ORDER BY chased_runs DESC
        LIMIT 1;
        """

    elif "show me the scorecard for match between CSK and MI" in question:
        return """
            WITH matched_matches AS (
                SELECT match_id
                FROM match_detail
                WHERE (team1_id = 'C.S.K-Team' AND team2_id = 'M.I-Team')
                   OR (team1_id = 'M.I-Team' AND team2_id = 'C.S.K-Team')
            )
            
            SELECT
                d.match_id,
                d.inning_num,
                p.player_name AS player,
                t.team_name,
                COUNT(*) AS balls_faced,
                SUM(d.runs_batsman) AS runs,
                SUM(CASE WHEN d.runs_batsman = 4 THEN 1 ELSE 0 END) AS fours,
                SUM(CASE WHEN d.runs_batsman = 6 THEN 1 ELSE 0 END) AS sixes
            FROM deliveries d
            JOIN players p ON d.batsman_id = p.player_id
            JOIN teams t ON d.batting_team_id = t.team_id
            WHERE d.match_id IN (SELECT match_id FROM matched_matches)
            GROUP BY d.match_id, d.inning_num, p.player_name, t.team_name
            ORDER BY d.match_id, d.inning_num, runs DESC;
        """

    elif "how many sixes were hit in the final" in question:
        return """
            SELECT 
            SUM(CASE WHEN d.runs_batsman = 6 THEN 1 ELSE 0 END) AS total_sixes_in_final
        FROM deliveries d
        JOIN match_detail md ON d.match_id = md.match_id
        WHERE md.stage = 'final';
        """

    elif "what was the winning margin in the closest match" in question:
        return """
            (
          SELECT 
            md.match_id,
            t1.team_name AS team1,
            t2.team_name AS team2,
            md.win_by_runs AS margin,
            'runs' AS margin_type
          FROM match_detail md
          JOIN teams t1 ON md.team1_id = t1.team_id
          JOIN teams t2 ON md.team2_id = t2.team_id
          WHERE md.win_by_runs > 0
          ORDER BY md.win_by_runs ASC
          LIMIT 1
        )
        UNION ALL
        (
          SELECT 
            md.match_id,
            t1.team_name AS team1,
            t2.team_name AS team2,
            md.win_by_wickets AS margin,
            'wickets' AS margin_type
          FROM match_detail md
          JOIN teams t1 ON md.team1_id = t1.team_id
          JOIN teams t2 ON md.team2_id = t2.team_id
          WHERE md.win_by_wickets > 0
          ORDER BY md.win_by_wickets ASC
          LIMIT 1
        );
        """

    elif "show partnerships over 100 runs" in question:
        return """
            WITH ordered_deliveries AS (
            SELECT
                d.match_id,
                d.inning_num,
                d.over_num,
                d.ball_num,
                d.batsman_id,
                d.non_striker_id,
                d.batting_team_id,
                d.runs_batsman + d.runs_extras AS runs,
                CASE WHEN w.wicket_id IS NOT NULL THEN 1 ELSE 0 END AS is_wicket,
                SUM(CASE WHEN w.wicket_id IS NOT NULL THEN 1 ELSE 0 END) 
                    OVER (PARTITION BY d.match_id, d.inning_num ORDER BY d.over_num, d.ball_num) AS partnership_num
            FROM deliveries d
            LEFT JOIN wickets w ON d.delivery_id = w.delivery_id
        ),
        
        partnership_runs AS (
            SELECT
                match_id,
                inning_num,
                partnership_num,
                batsman_id,
                non_striker_id,
                batting_team_id,
                SUM(runs) AS partnership_runs,
                COUNT(*) AS balls_faced
            FROM ordered_deliveries
            GROUP BY match_id, inning_num, partnership_num, batsman_id, non_striker_id, batting_team_id
        ),
        
        partnerships_with_names AS (
            SELECT
                pr.match_id,
                pr.inning_num,
                pr.partnership_num,
                t.team_name AS batting_team,
                p1.player_name AS batsman,
                p2.player_name AS non_striker,
                pr.partnership_runs,
                pr.balls_faced
            FROM partnership_runs pr
            JOIN players p1 ON pr.batsman_id = p1.player_id
            JOIN players p2 ON pr.non_striker_id = p2.player_id
            JOIN teams t ON pr.batting_team_id = t.team_id
        )
        
        SELECT *
        FROM partnerships_with_names
        WHERE partnership_runs >= 100
        ORDER BY partnership_runs DESC;
        """

    elif "which team has the best powerplay performance" in question:
        return """
            WITH powerplay_deliveries AS (
            SELECT
                d.match_id,
                d.inning_num,
                d.batting_team_id,
                d.runs_total,
                pp.start_over,
                pp.end_over
            FROM deliveries d
            JOIN powerplay pp
              ON d.match_id = pp.match_id
             AND d.inning_num = pp.inning_num
             AND d.over_num BETWEEN pp.start_over AND pp.end_over
        )
        SELECT
            t.team_name,
            SUM(pw.runs_total) AS total_powerplay_runs
        FROM powerplay_deliveries pw
        JOIN teams t ON pw.batting_team_id = t.team_id
        GROUP BY t.team_name
        ORDER BY total_powerplay_runs DESC
        LIMIT 1;
        """


    else:
        return None


@app.route("/query", methods=["POST"])
def query():
    user_question = request.json.get("question")
    logging.info(f"Received question: {user_question}")

    if not user_question:
        logging.warning("No question provided in request")
        return jsonify({"error": "No question provided"}), 400

    sql_query = map_question_to_sql(user_question)
    mapped_question = None

    if not sql_query:
        logging.info("No direct SQL mapping found, calling question_map")
        mapped_question = question_map(user_question)
        if mapped_question and mapped_question != "None":
            mapped_question = mapped_question.lower()
            logging.info(f"Mapped question via LLM: {mapped_question}")
            sql_query = map_question_to_sql(mapped_question)
        else:
            logging.info("LLM returned no suitable mapping")

    if not sql_query:
        logging.info("Trying fuzzy matching on user question")
        fuzzy_match_user = fuzzy_match_question(user_question)
        if fuzzy_match_user:
            logging.info(f"Fuzzy matched user question to: {fuzzy_match_user}")
            sql_query = map_question_to_sql(fuzzy_match_user)

        if not sql_query and mapped_question:
            logging.info("Trying fuzzy matching on mapped question")
            fuzzy_match_mapped = fuzzy_match_question(mapped_question)
            if fuzzy_match_mapped:
                logging.info(f"Fuzzy matched mapped question to: {fuzzy_match_mapped}")
                sql_query = map_question_to_sql(fuzzy_match_mapped)

    if not sql_query:
        logging.error("Unable to map question to SQL")
        return jsonify({"error": "Sorry, I don't understand that question yet."}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql_query)
        result = cursor.fetchall()
        cursor.close()
        conn.close()

        logging.info(f"Successfully executed query for question: {user_question}")
        return jsonify({
            "question": user_question,
            "mapped_question": mapped_question,
            "result": result
        })

    except mysql.connector.Error as err:
        logging.error(f"MySQL error: {err}")
        return jsonify({"error": str(err)}), 500



def run_flask():
    app.run(debug=True, port=5000, use_reloader=False)

Thread(target=run_flask).start()


# In[ ]:





# In[25]:


import requests

response = requests.post(
    "http://127.0.0.1:5000/query",
    json={"question": "highest run chase"}
)


(response.json())


# In[ ]:




