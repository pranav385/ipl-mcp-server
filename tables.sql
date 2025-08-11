-- DROP DATABASE IF EXISTS ipl_data;
-- CREATE DATABASE ipl_data;
-- USE ipl_data;

-- -- Drop tables in order of dependencies (child first)
-- DROP TABLE IF EXISTS powerplay;
-- DROP TABLE IF EXISTS wickets;
-- DROP TABLE IF EXISTS match_players;
-- DROP TABLE IF EXISTS replacements;
-- DROP TABLE IF EXISTS reviews;
-- DROP TABLE IF EXISTS deliveries;
-- DROP TABLE IF EXISTS match_officials;
-- DROP TABLE IF EXISTS officials;
-- DROP TABLE IF EXISTS match_detail;
-- DROP TABLE IF EXISTS players_team;
-- DROP TABLE IF EXISTS players;
-- DROP TABLE IF EXISTS teams;

-- -- 1. TEAMS
-- CREATE TABLE teams (
--     team_id VARCHAR(50) PRIMARY KEY,
--     team_name VARCHAR(250) NOT NULL UNIQUE
-- );

-- -- 2. PLAYERS
-- CREATE TABLE players (
--     player_id VARCHAR(100) PRIMARY KEY,
--     player_name VARCHAR(200) NOT NULL,
--     substitute BOOL DEFAULT FALSE
-- );

--     -- 2_1. Player_team
-- CREATE TABLE players_team (
--     player_id VARCHAR(100) NOT NULL,
--     team_id VARCHAR(50) NOT NULL,
--     season YEAR NOT NULL,
--     PRIMARY KEY (player_id, team_id, season),
--     FOREIGN KEY (player_id) REFERENCES players(player_id),
--     FOREIGN KEY (team_id) REFERENCES teams(team_id)
-- );

-- -- 3. MATCH DETAILS
-- CREATE TABLE match_detail (
--     match_id VARCHAR(100) PRIMARY KEY,
--     match_date DATE NOT NULL,
--     city VARCHAR(100) NOT NULL,
--     venue VARCHAR(300),
--     match_number INT,
--     stage VARCHAR(100),
--     match_type VARCHAR(50) NOT NULL,
--     gender ENUM('male','female') NOT NULL,
--     event_name VARCHAR(100),
--     balls_per_over INT DEFAULT 6 CHECK (balls_per_over > 0),
--     overs INT CHECK (overs > 0),
--     season YEAR NOT NULL,
--     team_type VARCHAR(75) NOT NULL,
--     
--     team1_id VARCHAR(50) NOT NULL,
--     team2_id VARCHAR(50) NOT NULL,
--     toss_winner_team_id VARCHAR(50) NOT NULL,
--     toss_decision VARCHAR(20) NOT NULL,
--     winner_team_id VARCHAR(50),
--     
--     win_by_runs INT DEFAULT NULL CHECK (win_by_runs >= 0),
--     win_by_wickets INT DEFAULT NULL CHECK (win_by_wickets >= 0),

--     player_of_match_id VARCHAR(100),

--     FOREIGN KEY (player_of_match_id) REFERENCES players(player_id),
--     FOREIGN KEY (team1_id) REFERENCES teams(team_id),
--     FOREIGN KEY (team2_id) REFERENCES teams(team_id),
--     FOREIGN KEY (toss_winner_team_id) REFERENCES teams(team_id),
--     FOREIGN KEY (winner_team_id) REFERENCES teams(team_id),

--     CHECK (team1_id <> team2_id),
--     CHECK (winner_team_id IS NULL OR winner_team_id = team1_id OR winner_team_id = team2_id)
-- );


-- -- 4. OFFICIALS
-- CREATE TABLE officials (
--     official_id VARCHAR(150) PRIMARY KEY,
--     official_name VARCHAR(150) NOT NULL
-- );

-- -- 5. MATCH OFFICIALS
-- CREATE TABLE match_officials (
--     match_id VARCHAR(75),
--     official_id VARCHAR(150) NOT NULL,
--     roles VARCHAR(100) NOT NULL,

--     PRIMARY KEY (match_id, official_id, roles),

--      FOREIGN KEY (match_id) REFERENCES match_detail(match_id),
--     FOREIGN KEY (official_id) REFERENCES officials(official_id)
-- );

-- -- 6. DELIVERIES DETAIL
-- CREATE TABLE deliveries (
--     delivery_id VARCHAR(100) PRIMARY KEY,
--     match_id VARCHAR(75) NOT NULL,
--     inning_num INT NOT NULL CHECK (inning_num > 0),
--     batting_team_id VARCHAR(50) NOT NULL,
--     bowling_team_id VARCHAR(50) NOT NULL,
--     over_num INT NOT NULL CHECK (over_num >= 0),
--     ball_num INT NOT NULL CHECK (ball_num >= 0),
--         
--     batsman_id VARCHAR(75) NOT NULL,
--     bowler_id VARCHAR(75) NOT NULL,
--     non_striker_id VARCHAR(75) NOT NULL,
--     
--     runs_batsman INT NOT NULL DEFAULT 0 CHECK (runs_batsman >= 0),
--     runs_extras INT NOT NULL DEFAULT 0 CHECK (runs_extras >= 0),
--     runs_total INT NOT NULL DEFAULT 0 CHECK (runs_total >= 0),
--     
--     extras_type VARCHAR(50),
--     extras_runs INT DEFAULT 0 CHECK (extras_runs >= 0),

--     FOREIGN KEY (match_id) REFERENCES match_detail(match_id),
--     FOREIGN KEY (batting_team_id) REFERENCES teams(team_id),
--     FOREIGN KEY (bowling_team_id) REFERENCES teams(team_id),
--     FOREIGN KEY (batsman_id) REFERENCES players(player_id),
--     FOREIGN KEY (bowler_id) REFERENCES players(player_id),
--     FOREIGN KEY (non_striker_id) REFERENCES players(player_id)
-- );


-- -- 7. Reviews
-- CREATE TABLE reviews (
--     review_id VARCHAR(200) PRIMARY KEY,
--     match_id VARCHAR(75) NOT NULL,
--     delivery_id VARCHAR(100) NOT NULL,
--     
--     review_by_team_id VARCHAR(50) NOT NULL,
--     umpire_id VARCHAR(150),
--     batsman_name_id VARCHAR(75),
--     decision VARCHAR(50) NOT NULL,
--     review_type VARCHAR(50) NOT NULL,
--     umpires_call VARCHAR(10),

--     FOREIGN KEY (match_id) REFERENCES match_detail(match_id),
--     FOREIGN KEY (delivery_id) REFERENCES deliveries(delivery_id),
--     FOREIGN KEY (review_by_team_id) REFERENCES teams(team_id),
--     FOREIGN KEY (batsman_name_id) REFERENCES players(player_id),
--     FOREIGN KEY (umpire_id) REFERENCES officials(official_id)
-- );


-- -- 8. Replacements
-- CREATE TABLE replacements (
--     replacement_id VARCHAR(200) PRIMARY KEY,
--     match_id VARCHAR(75) NOT NULL,

--     team_id VARCHAR(50) NOT NULL,
--     player_in_id VARCHAR(75) NOT NULL,
--     player_out_id VARCHAR(75) NOT NULL,
--     reason VARCHAR(100),

--     FOREIGN KEY (match_id) REFERENCES match_detail(match_id),
--     FOREIGN KEY (team_id) REFERENCES teams(team_id),
--     FOREIGN KEY (player_in_id) REFERENCES players(player_id),
--     FOREIGN KEY (player_out_id) REFERENCES players(player_id)
-- );


-- -- 9. Match Players
-- CREATE TABLE match_players (
--     match_id VARCHAR(75) NOT NULL,
--     player_id VARCHAR(75) NOT NULL,
--     team_id VARCHAR(50) NOT NULL,

--     PRIMARY KEY (match_id, player_id),

--     FOREIGN KEY (match_id) REFERENCES match_detail(match_id),
--     FOREIGN KEY (player_id) REFERENCES players(player_id),
--     FOREIGN KEY (team_id) REFERENCES teams(team_id)
-- );


-- -- 10. Wickets
-- CREATE TABLE wickets (
--     wicket_id varchar(200) PRIMARY KEY,
--     delivery_id VARCHAR(100) NOT NULL,
--     player_dismissed_id VARCHAR(75) NOT NULL,
--     dismissal_kind VARCHAR(50) NOT NULL,
--     fielder_id VARCHAR(75),
--     
--    FOREIGN KEY (player_dismissed_id) REFERENCES players(player_id),
--     FOREIGN KEY (fielder_id) REFERENCES players(player_id),
--     FOREIGN KEY (delivery_id) REFERENCES deliveries(delivery_id)

--     );
--     
--     -- Powerplay
--     CREATE TABLE powerplay (
--     powerplay_id varchar(200) PRIMARY KEY,
--     match_id VARCHAR(75) NOT NULL,
--     inning_num INT NOT NULL CHECK (inning_num > 0),
--     start_over INT,
--     end_over int,
--     pp_type varchar(10),
--     
--     FOREIGN KEY (match_id) REFERENCES match_detail(match_id)
--     );
--     

--     

