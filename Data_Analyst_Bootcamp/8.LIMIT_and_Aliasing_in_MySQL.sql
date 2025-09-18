
--

-- LIMIT 2 rows
SELECT *
FROM Parks_and_Recreation.employee_demographics
ORDER BY age DESC
LIMIT 3
;

-- Starting at the 3rd row, and count 2 rows
SELECT *
FROM Parks_and_Recreation.employee_demographics
ORDER BY age DESC
LIMIT 3, 2
;

-- Aliasing
SELECT 
  gender,
  AVG(age) as avg_age
FROM
  Parks_and_Recreation.employee_demographics
GROUP BY gender
HAVING avg_age > 40;
