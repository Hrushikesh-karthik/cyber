CREATE DATABASE vulnscanner;
USE vulnscanner;

CREATE TABLE scan_result (
  id INT AUTO_INCREMENT PRIMARY KEY,
  target_url VARCHAR(255),
  result TEXT,
  summary TEXT,
  scan_date DATETIME
);
