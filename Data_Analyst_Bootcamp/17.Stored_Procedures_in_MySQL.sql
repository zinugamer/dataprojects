/*
    Stored Procedures: 储存已有的query过程，可以直接调用
      - 有时可以在最顶端声明USE Parks_and_Recreation，表示用的是哪个database
      - DROP PROCEDURE IF EXISTS procedure_name 防止过去定义过;

*/

-- (1) 创建procedure & 调用procedure

CREATE PROCEDURE large_salaries()
SELECT *
FROM Parks_and_Recreation.employee_salary
WHERE salary >= 50000;

CALL large_salaries();

-- (2) DELIMITER: 在同一个PROCEDURE创建多个query（通常只保存第一个）
DELIMITER $$
CREATE PROCEDURE large_salaries3()
BEGIN
    SELECT *
    FROM Parks_and_Recreation.employee_salary
    WHERE salary >= 50000;
    SELECT *
    FROM Parks_and_Recreation.employee_salary
    WHERE salary >= 10000;
END $$ 
DELIMITER ;

CALL large_salaries3();


-- (3) parameters as inputs for a PROCEDURE
USE parks_and_recreation;
DROP PROCEDURE IF EXISTS large_salaries4;
DELIMITER $$
CREATE PROCEDURE large_salaries4(begin_date date, end_date date)
BEGIN
    SELECT 
      employee_id,
      CONCAT(first_name, ' ', last_name) full_name,
      gender,
      age,
      birth_date
	FROM employee_demographics
    WHERE birth_date BETWEEN begin_date AND end_date;
END$$
DELIMITER ;
-- Call the query we created within this procedure, by typing inputs
CALL large_salaries4('1969-01-01', '1980-12-31');