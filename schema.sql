CREATE DATABASE IF NOT EXISTS db_name;
USE db_name;

CREATE TABLE IF NOT EXISTS book (
    `SL.NO` VARCHAR(50) NOT NULL,
    `A/c No` VARCHAR(50) NOT NULL,
    `Title` VARCHAR(255) NOT NULL,
    `Author` VARCHAR(255) NOT NULL,
    `Edition/Year` VARCHAR(100) NOT NULL,
    `Publication` VARCHAR(255) NOT NULL,
    `Issue_status` ENUM('Available', 'Unavailable') NOT NULL DEFAULT 'Available',
    `return_date` DATE NULL,
    PRIMARY KEY (`A/c No`),
    UNIQUE KEY `unique_sl_no` (`SL.NO`)
);

CREATE TABLE IF NOT EXISTS issue (
    `id` INT NOT NULL AUTO_INCREMENT,
    `Student_Name` VARCHAR(255) NOT NULL,
    `Reg_no` VARCHAR(100) NOT NULL,
    `AC_No` VARCHAR(50) NOT NULL,
    `Title` VARCHAR(255) NOT NULL,
    `Author` VARCHAR(255) NOT NULL,
    `Issue_Date` DATE NOT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_issue_ac_no` (`AC_No`)
);

CREATE TABLE IF NOT EXISTS returnb (
    `id` INT NOT NULL AUTO_INCREMENT,
    `Student_Name` VARCHAR(255) NOT NULL,
    `Reg_no` VARCHAR(100) NOT NULL,
    `AC_No` VARCHAR(50) NOT NULL,
    `Title` VARCHAR(255) NOT NULL,
    `Author` VARCHAR(255) NOT NULL,
    `Return_Date` DATE NOT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_return_ac_no` (`AC_No`)
);
