
/*
  Unions
*/
-- 直接union会以上面的table字段作为 行表头，两个table上下拼接，但字段对应不上
SELECT *
FROM Parks_and_Recreation.employee_demographics
UNION
SELECT *
FROM Parks_and_Recreation.employee_salary;

-- UNION DISTINCT: 正确方式是两个tables选择相同的字段拼接，union自动去重
SELECT first_name, last_name
FROM Parks_and_Recreation.employee_demographics
UNION DISTINCT
SELECT first_name, last_name
FROM Parks_and_Recreation.employee_salary;

-- UNION ALL: 允许duplicates，全部合并records
SELECT first_name, last_name
FROM Parks_and_Recreation.employee_demographics
UNION ALL
SELECT first_name, last_name
FROM Parks_and_Recreation.employee_salary;

-- Multiple Unions, based on WHERE conditions
SELECT first_name, last_name, 'Old Man' AS label
FROM Parks_and_Recreation.employee_demographics
WHERE age > 40 AND gender = 'Male'
UNION
SELECT first_name, last_name, 'Old Lady' AS label
FROM Parks_and_Recreation.employee_demographics
WHERE age > 40 AND gender = 'Female'
UNION 
SELECT first_name, last_name, 'Highly Paid Employee' AS label
FROM Parks_and_Recreation.employee_salary
WHERE salary > 70000
ORDER BY 1,2
;