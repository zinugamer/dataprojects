/*
  Specify the name of database before the table name
*/
SELECT *
FROM parks_and_recreation.employee_demographics;

SELECT *
FROM parks_and_recreation.employee_salary;

-- Calculations within Select Statements ('PEMDAS' operations order)
SELECT 
  first_name, 
  last_name, 
  birth_date,
  age,
  (age+10)*10 AS calculated_age
FROM Parks_and_Recreation.employee_demographics;

-- keyword 'DISTINCT' only works for the first 
SELECT
  DISTINCT first_name, gender
FROM
  Parks_and_Recreation.employee_demographics;