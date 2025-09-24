/*
  WHERE Clause
*/

SELECT *
FROM Parks_and_Recreation.employee_salary
WHERE first_name = 'Leslie';

SELECT *
FROM Parks_and_Recreation.employee_salary
WHERE salary>=50000;

SELECT *
FROM Parks_and_Recreation.employee_demographics
WHERE gender != 'Female';

SELECT *
FROM Parks_and_Recreation.employee_demographics
WHERE birth_date > '1985-01-01';
/*
  Logical Operators: AND OR NOT
*/

SELECT *
FROM Parks_and_Recreation.employee_demographics
WHERE birth_date > '1985-01-01'
AND gender = 'male';
-- complex example
SELECT *
FROM Parks_and_Recreation.employee_demographics
WHERE birth_date > '1985-01-01'
OR NOT gender = 'male';
-- complex example
SELECT *
FROM Parks_and_Recreation.employee_demographics
WHERE (first_name='Leslie' AND age=44) OR age > 55;

-- LIKE statement
SELECT *
FROM Parks_and_Recreation.employee_demographics
WHERE first_name LIKE '%er%';

SELECT *
FROM Parks_and_Recreation.employee_demographics
WHERE first_name LIKE 'a%';

-- underscores within '' after LIKE, means one empty letter position
SELECT *
FROM Parks_and_Recreation.employee_demographics
WHERE first_name LIKE 'a__';

SELECT *
FROM Parks_and_Recreation.employee_demographics
WHERE first_name LIKE 'a___%';

SELECT *
FROM Parks_and_Recreation.employee_demographics
WHERE birth_date LIKE '1989%';
