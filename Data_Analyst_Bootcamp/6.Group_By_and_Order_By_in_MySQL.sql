/*
  GROUP BY
*/

-- (1) aggregated column 'gender'
SELECT gender
FROM Parks_and_Recreation.employee_demographics
GROUP BY gender
;
-- (2) cannot select a non-aggregated column (that is not in group by)
/*
SELECT first_name
FROM Parks_and_Recreation.employee_demographics
GROUP BY gender;
*/

-- (3) 
SELECT gender, AVG(age) AS avg_age
FROM Parks_and_Recreation.employee_demographics
GROUP BY gender;


-- (4) distinct values of a column
SELECT occupation, ROUND(AVG(salary),0) AS avg_salary
FROM Parks_and_Recreation.employee_salary
GROUP BY occupation;

-- (5) 
SELECT 
  gender, 
  AVG(age) AS avg_age, 
  MAX(age) AS max_age, 
  MIN(age) AS min_age, 
  COUNT(age) AS cnt_age
FROM Parks_and_Recreation.employee_demographics
GROUP BY gender;

/*
  ORDER BY
*/
SELECT *
FROM Parks_and_Recreation.employee_demographics
ORDER BY first_name DESC;

-- 
SELECT *
FROM Parks_and_Recreation.employee_demographics
ORDER BY gender, age;

SELECT *
FROM Parks_and_Recreation.employee_demographics
ORDER BY age, gender;


-- DESC only works on the nearest columnname
SELECT *
FROM Parks_and_Recreation.employee_demographics
ORDER BY gender, age DESC;

--
SELECT *
FROM Parks_and_Recreation.employee_demographics
ORDER BY 4,5;

