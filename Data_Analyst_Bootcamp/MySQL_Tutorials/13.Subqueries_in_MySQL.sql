/*
  Subqueries

*/

-- (1) Subquery in a WHERE clause
SELECT *
FROM Parks_and_Recreation.employee_demographics
WHERE employee_id IN (
				  SELECT employee_id
                  FROM Parks_and_Recreation.employee_salary
                  WHERE dept_id = 1)
;

-- (2) Subquery in a SELECT statement

SELECT 
  first_name,
  salary,
  AVG(salary) as avg_salary
FROM Parks_and_Recreation.employee_salary
GROUP BY first_name, salary
;

SELECT 
  CONCAT(first_name, ' ', last_name) as employees, 
  salary,
  (SELECT AVG(salary) FROM Parks_and_Recreation.employee_salary) as avg_salary
FROM Parks_and_Recreation.employee_salary
ORDER BY avg_salary
;

WITH a AS (
  SELECT 
  CONCAT(first_name, ' ', last_name) as employees, 
  salary,
  (SELECT AVG(salary) FROM Parks_and_Recreation.employee_salary) as avg_salary
  FROM Parks_and_Recreation.employee_salary
)
SELECT 
  employees, 
  salary,
  CASE
    WHEN (salary > avg_salary) THEN 'higher'
    WHEN (salary < avg_salary) THEN 'below'
    ELSE 'median'
  END AS comparison
FROM a
;

-- (3) Derived table must have its own name
SELECT
  gender,
  AVG(age),
  MAX(age),
  MIN(age),
  COUNT(age),
  COUNT(DISTINCT age)
FROM Parks_and_Recreation.employee_demographics
GROUP BY gender
;


SELECT *
FROM (
  SELECT
    gender,
    AVG(age),
    MAX(age),
    MIN(age),
    COUNT(age),
    COUNT(DISTINCT age)
  FROM Parks_and_Recreation.employee_demographics
  GROUP BY gender) AS derived_table
;

SELECT 
  ROUND(AVG(max_age),2) as avg_max_age -- AVG(`MAX(age)`)
FROM (
  SELECT
    gender,
    AVG(age) as avg_age, 
    MAX(age) as max_age,
    MIN(age) as min_age,
    COUNT(age) as cnt_age,
    COUNT(DISTINCT age) as cnt_distinct_age
  FROM Parks_and_Recreation.employee_demographics
  GROUP BY gender) AS aggregated_table
;

