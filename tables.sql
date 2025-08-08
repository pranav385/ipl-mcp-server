CREATE DATABASE cric_data;
USE cric_data;

-- 1. TEAMS
CREATE TABLE teams (
    team_id VARCHAR(50) PRIMARY KEY,
    team_name VARCHAR(250) NOT NULL UNIQUE
);

-- 2. PLAYERS
CREATE TABLE players (
    player_id VARCHAR(100) PRIMARY KEY,
    player_name VARCHAR(200) NOT NULL,
    team_name VARCHAR(250) NOT NULL
);

-- 3. MATCH DETAILS
CREATE TABLE match_detail (
    match_id VARCHAR(100) PRIMARY KEY,
    match_date DATETIME NOT NULL,
    city VARCHAR(100) NOT NULL,
    venue VARCHAR(300),
    match_number INT ,
    stage varchar(100),
    match_type varchar(50) NOT NULL,
    gender ENUM('male','female') NOT NULL,
    event_name VARCHAR(100),
    balls_per_over INT DEFAULT 6 CHECK (balls_per_over > 0),
    overs INT CHECK (overs > 0),
    season YEAR NOT NULL,
    team_type VARCHAR(75) NOT NULL,
    
    team_1 VARCHAR(250) NOT NULL,
    team_2 VARCHAR(250) NOT NULL,
    toss_winner_team VARCHAR(250) NOT NULL,
    toss_decision varchar(20) NOT NULL,
    winner_team VARCHAR(250),
    
    win_by_runs INT DEFAULT NULL CHECK (win_by_runs >= 0),
	win_by_wickets INT DEFAULT NULL CHECK (win_by_wickets >= 0),

    player_of_match_id VARCHAR(100),

    FOREIGN KEY (player_of_match_id) REFERENCES players(player_id),

    CHECK (team_1 <> team_2),
    CHECK (winner_team IS NULL OR winner_team = team_1 OR winner_team = team_2)
);

-- 4. OFFICIALS
CREATE TABLE officials (
    official_id VARCHAR(150) PRIMARY KEY,
    official_name VARCHAR(150) NOT NULL
);

-- 5. MATCH OFFICIALS
CREATE TABLE match_officials (
    match_id VARCHAR(75),
    official_id VARCHAR(150) NOT NULL,
    roles VARCHAR(100) NOT NULL,

    PRIMARY KEY (match_id, official_id, roles),

     FOREIGN KEY (match_id) REFERENCES match_detail(match_id),
    FOREIGN KEY (official_id) REFERENCES officials(official_id)
);

-- 6. DELIVERIES DETAIL
CREATE TABLE deliveries (
    delivery_id VARCHAR(100) PRIMARY KEY,
    match_id VARCHAR(75) NOT NULL,
    inning_num INT NOT NULL CHECK (inning_num > 0),
    batting_team VARCHAR(150) NOT NULL,
    bowling_team VARCHAR(150) NOT NULL,
    over_num INT NOT NULL CHECK (over_num >= 0),
    ball_num INT NOT NULL CHECK (ball_num >= 0),
        
    batsman_id VARCHAR(75) NOT NULL,
    bowler_id VARCHAR(75) NOT NULL,
    non_striker_id VARCHAR(75) NOT NULL,
    
    runs_batsman INT NOT NULL DEFAULT 0 CHECK (runs_batsman >= 0),
    runs_extras INT NOT NULL DEFAULT 0 CHECK (runs_extras >= 0),
    runs_total INT NOT NULL DEFAULT 0 CHECK (runs_total >= 0),
    
    extras_type VARCHAR(50),
    extras_runs INT DEFAULT 0 CHECK (extras_runs >= 0),

      FOREIGN KEY (match_id) REFERENCES match_detail(match_id),
    FOREIGN KEY (batsman_id) REFERENCES players(player_id),
    FOREIGN KEY (bowler_id) REFERENCES players(player_id),
    FOREIGN KEY (non_striker_id) REFERENCES players(player_id)

);

-- 7. Reviews
CREATE TABLE reviews (
    review_id varchar(200) PRIMARY KEY,
    match_id VARCHAR(75) NOT NULL,
    delivery_id VARCHAR(100) NOT NULL,
    
    review_by_team VARCHAR(250) NOT NULL,
    umpire_id VARCHAR(150),
    batsman_name_id VARCHAR(75),
    decision varchar(50) NOT NULL,
    review_type varchar(50) NOT NULL,
    umpires_call varchar(10),

    FOREIGN KEY (match_id) REFERENCES match_detail(match_id),
    FOREIGN KEY (delivery_id) REFERENCES deliveries(delivery_id),
    FOREIGN KEY (batsman_name_id) REFERENCES players(player_id),
    FOREIGN KEY (umpire_id) REFERENCES officials(official_id)

);

-- 8. Replacements
CREATE TABLE replacements (
    replacement_id varchar(200) PRIMARY KEY,
    match_id VARCHAR(75) NOT NULL,

    team_name VARCHAR(250) NOT NULL,
    player_in_id VARCHAR(75) NOT NULL,
    player_out_id VARCHAR(75) NOT NULL,
    reason VARCHAR(100),

    FOREIGN KEY (match_id) REFERENCES match_detail(match_id),
    FOREIGN KEY (player_in_id) REFERENCES players(player_id),
    FOREIGN KEY (player_out_id) REFERENCES players(player_id)

);

-- 9. Match Players
CREATE TABLE match_players (
    match_id VARCHAR(75) NOT NULL,
    player_id VARCHAR(75) NOT NULL,
    team_name varchar(100) NOT NULL,

    PRIMARY KEY (match_id, player_id),

    FOREIGN KEY (match_id) REFERENCES match_detail(match_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id)

);

-- 10. Wickets
CREATE TABLE wickets (
    wicket_id varchar(200) PRIMARY KEY,
    delivery_id VARCHAR(100) NOT NULL,
    player_dismissed_id VARCHAR(75) NOT NULL,
    dismissal_kind VARCHAR(50) NOT NULL,
    fielder_id VARCHAR(75),
    
   FOREIGN KEY (player_dismissed_id) REFERENCES players(player_id),
    FOREIGN KEY (fielder_id) REFERENCES players(player_id),
    FOREIGN KEY (delivery_id) REFERENCES deliveries(delivery_id)

    );
    

