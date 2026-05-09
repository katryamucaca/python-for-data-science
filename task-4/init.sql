CREATE DATABASE IF NOT EXISTS my_database;
USE my_database;

-- create titanic table with correct column types
CREATE TABLE IF NOT EXISTS titanic (
    PassengerId INT,
    Survived    INT,
    Pclass      INT,
    Name        VARCHAR(255),
    Sex         VARCHAR(10),
    Age         FLOAT,
    SibSp       INT,
    Parch       INT,
    Ticket      VARCHAR(50),
    Fare        FLOAT,
    Cabin       VARCHAR(50),
    Embarked    VARCHAR(5)
);

-- load csv, replace empty strings with NULL for Age, Cabin, Embarked
LOAD DATA INFILE '/var/lib/mysql-files/titanic.csv'
INTO TABLE titanic
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(PassengerId, Survived, Pclass, Name, Sex, @Age, SibSp, Parch, Ticket, Fare, @Cabin, @Embarked)
SET
    Age      = NULLIF(@Age, ''),
    Cabin    = NULLIF(@Cabin, ''),
    Embarked = NULLIF(@Embarked, '');