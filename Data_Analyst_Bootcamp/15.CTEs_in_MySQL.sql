/*
    CTEs: Similar to a subquery

*/

-- CTE is not a permenant object(like a temp table), can be only queried in one query

-- (1)
WITH CTE_Example AS (
SELECT 
  dem.employee_id,
  dem.first_name,
  dem.last_name,
  gender,
  birth_date,
  salary
FROM Parks_and_Recreation.employee_demographics dem
JOIN Parks_and_Recreation.employee_salary sal
    ON dem.employee_id = sal.employee_id
)

SELECT 
  employee_id,
  birth_date,
  salary
FROM CTE_Example
;

-- (2)
WITH CTE_Example_2 AS (
SELECT 
  gender,
  avg(salary) avg_sal,
  max(salary) max_sal,
  min(salary) min_sal,
  count(salary) cnt_sal
FROM Parks_and_Recreation.employee_demographics dem
JOIN Parks_and_Recreation.employee_salary sal
    ON dem.employee_id = sal.employee_id
GROUP BY gender
)

SELECT 
  gender,
  CONCAT("$",ROUND(avg_sal,2)) average_salary
FROM CTE_Example_2
;
-- (3) 
WITH CTE_1 AS (
SELECT
  employee_id, 
  gender,
  birth_date
FROM Parks_and_Recreation.employee_demographics
WHERE birth_date > '1985-01-01'
),

CTE_2 AS (
SELECT
  employee_id,
  salary
FROM Parks_and_Recreation.employee_salary
WHERE salary > 50000
)
SELECT *
FROM CTE_1
JOIN CTE_2
    ON CTE_1.employee_id = CTE_2.employee_id
;

-- (4) Rename cols right after the CTE name
WITH CTE_3 (Gender, AVG_Sal, MAX_Sal, MIN_Sal, COUNT_Sal) AS
(
SELECT 
  gender,
  AVG(salary) avg_sal,
  MAX(salary) max_sal,
  MIN(salary) min_sal,
  COUNT(salary) cnt_sal
FROM Parks_and_Recreation.employee_demographics dem
JOIN Parks_and_Recreation.employee_salary sal
    ON dem.employee_id = sal.employee_id
GROUP BY gender
)
SELECT *
FROM CTE_3
;




)