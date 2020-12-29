DROP DATABASE IF EXISTS ttd_club_activities;
CREATE DATABASE ttd_club_activities;

\! echo --Databases---------------------
SHOW DATABASES;
\! echo

USE ttd_club_activities;
GRANT ALL PRIVILEGES ON ttd_club_activities.* TO 'clubfitness_user'@'localhost' IDENTIFIED BY 'Mydoghasnonose13!' WITH GRANT OPTION;
FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON ttd_club_activities.* TO 'clubfitness_user'@'10.0.0.0/255.255.255.0' IDENTIFIED BY 'Mydoghasnonose13!' WITH GRANT OPTION;
FLUSH PRIVILEGES;


\! echo --Creating club activity table-------
CREATE TABLE club_activity (
  id INT NOT NULL AUTO_INCREMENT,
  activityID BIGINT NOT NULL,
  athlete TEXT NOT NULL,
  data_updated_at BIGINT NOT NULL,
  elapsed_time INT NOT NULL,
  distance DECIMAL(5,2) NOT NULL,
  name TEXT NOT NULL,
  created_date DATETIME NOT NULL,
  start_date_local DATETIME NOT NULL,
  PRIMARY KEY (id)		    
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
\! echo
\! echo --Decription - bargain_item ------
DESCRIBE club_activity;

\! echo
\! echo --Tables-----------------------
SHOW tables;
