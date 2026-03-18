CREATE DATABASE IF NOT EXISTS data_literacy_game
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE data_literacy_game;

CREATE TABLE IF NOT EXISTS levels (
  id INT AUTO_INCREMENT PRIMARY KEY,
  level_code VARCHAR(50) NOT NULL UNIQUE,
  title VARCHAR(255) NOT NULL,
  difficulty VARCHAR(50),
  sort_order INT NOT NULL DEFAULT 0,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  config_file VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_progress (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id VARCHAR(64) NOT NULL,
  current_level_code VARCHAR(50) NOT NULL,
  unlocked_levels_json JSON NOT NULL,
  read_items_json JSON NULL,
  decision_draft_json JSON NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uniq_user_progress (user_id)
);

CREATE TABLE IF NOT EXISTS level_results (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id VARCHAR(64) NOT NULL,
  level_code VARCHAR(50) NOT NULL,
  status VARCHAR(20) NOT NULL,
  fail_type VARCHAR(50) NULL,
  score INT NULL,
  decision_payload_json JSON NULL,
  completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS certificate_records (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id VARCHAR(64) NOT NULL,
  certificate_no VARCHAR(100) NOT NULL UNIQUE,
  total_score INT NOT NULL,
  issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO levels (level_code, title, difficulty, sort_order, config_file)
VALUES
('level_1', '生鲜蔬果损耗危机', 'easy', 1, 'level_1.json')
ON DUPLICATE KEY UPDATE
  title = VALUES(title),
  difficulty = VALUES(difficulty),
  sort_order = VALUES(sort_order),
  config_file = VALUES(config_file);
