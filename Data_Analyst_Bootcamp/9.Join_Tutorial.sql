/*
  Joins
*/
-- INNER JOIN (JOIN) 如果两个表有相同字段，会造成重复列。因此在select中加上具体table
SELECT dem.employee_id, dem.first_name, dem.last_name, dem.age, sal.occupation
FROM Parks_and_Recreation.employee_demographics AS dem
JOIN Parks_and_Recreation.employee_salary AS sal
    ON dem.employee_id = sal.employee_id;
    
-- Outer joins
-- LEFT JOIN
SELECT *
FROM Parks_and_Recreation.employee_demographics AS dem
LEFT JOIN Parks_and_Recreation.employee_salary AS sal
    ON dem.employee_id = sal.employee_id;
-- RIGHT JOIN
SELECT *
FROM Parks_and_Recreation.employee_demographics AS dem
RIGHT JOIN Parks_and_Recreation.employee_salary AS sal
    ON dem.employee_id = sal.employee_id;
    
-- Self Join
SELECT 
  emp1.employee_id AS emp_santa,
  emp1.first_name AS first_name_santa,
  emp1.last_name AS last_name_santa,
  emp2.employee_id AS emp_name,
  emp2.first_name AS first_name_emp,
  emp2.last_name AS last_name_emp
FROM Parks_and_Recreation.employee_salary AS emp1
JOIN Parks_and_Recreation.employee_salary AS emp2
    ON emp1.employee_id + 1 = emp2.employee_id;
    
/* 
  Joining multiple tables together
*/

SELECT *
FROM Parks_and_Recreation.employee_demographics AS dem
INNER JOIN Parks_and_Recreation.employee_salary AS sal
    ON dem.employee_id = sal.employee_id
INNER JOIN Parks_and_Recreation.parks_departments AS pd
    ON sal.dept_id = pd.department_id;

-- 选择具体字段，避免输出重复列
SELECT 
  dem.employee_id,
  dem.first_name,
  dem.last_name,
  sal.salary,
  pd.department_name
FROM Parks_and_Recreation.employee_demographics AS dem
INNER JOIN Parks_and_Recreation.employee_salary AS sal
    ON dem.employee_id = sal.employee_id
INNER JOIN Parks_and_Recreation.parks_departments AS pd
    ON sal.dept_id = pd.department_id;

