/*
    Window Functions

*/

-- (1) OVER()
-- 对比看：GROUP BY对每个性别计算average salary
SELECT 
  gender, 
  ROUND(AVG(salary),2) as avg_salary
FROM 
  Parks_and_Recreation.employee_demographics dem
JOIN Parks_and_Recreation.employee_salary sal
  ON dem.employee_id = sal.employee_id
GROUP BY gender
;

-- OVER():对每个record都计算average salary
SELECT 
  dem.first_name,
  gender, 
  salary,
  ROUND(AVG(salary) OVER(), 2) as overall_avg_salary
FROM 
  Parks_and_Recreation.employee_demographics dem
JOIN Parks_and_Recreation.employee_salary sal
  ON dem.employee_id = sal.employee_id
;

-- (2) OVER(PARTITION BY)
-- OVER(PARTITION BY gender): 把records按gender虚拟分组后计算average salary
SELECT
  dem.first_name,
  dem.last_name,
  gender,
  salary,
  AVG(salary) OVER(PARTITION BY gender) as avg_salary_by_gender
FROM Parks_and_Recreation.employee_demographics dem
JOIN Parks_and_Recreation.employee_salary sal
  ON dem.employee_id = sal.employee_id
;

-- (3) SUM() & OVER
-- Total
SELECT
  dem.first_name,
  dem.last_name,
  gender,
  salary,
  SUM(salary) OVER(PARTITION BY gender) as total_salary_by_gender
FROM Parks_and_Recreation.employee_demographics dem
JOIN Parks_and_Recreation.employee_salary sal
  ON dem.employee_id = sal.employee_id
;
-- Rolling total: SUM(salary) OVER(PARTITION BY gender ORDER BY dem.employee_id)  
SELECT
  dem.first_name,
  dem.last_name,
  gender,
  salary,
  SUM(salary) OVER(PARTITION BY gender ORDER BY dem.employee_id) as total_salary_by_gender
FROM Parks_and_Recreation.employee_demographics dem
JOIN Parks_and_Recreation.employee_salary sal
  ON dem.employee_id = sal.employee_id
;
-- (4) ROW_NUMBER() & RANK()
-- 行序号不能重复 no duplications，但是排序会在相同数值时给出相同的序号并且跳过下个序号 assign the same nun
SELECT
  dem.first_name,
  dem.last_name,
  gender,
  salary,
  ROW_NUMBER() OVER(PARTITION BY gender ORDER BY salary DESC) as row_num,
  RANK() OVER(PARTITION BY gender ORDER BY salary DESC) as rank_num
FROM Parks_and_Recreation.employee_demographics dem
JOIN Parks_and_Recreation.employee_salary sal
  ON dem.employee_id = sal.employee_id
;
-- DENSE_RANK(): 类似RANK()但是不会在存在相同数值的record出现后跳过下个序号
SELECT
  dem.first_name,
  dem.last_name,
  gender,
  salary,
  ROW_NUMBER() OVER(PARTITION BY gender ORDER BY salary DESC) as row_num,
  RANK() OVER(PARTITION BY gender ORDER BY salary DESC) as rank_num,
  DENSE_RANK() OVER(PARTITION BY gender ORDER BY salary DESC) as dense_rank_num
FROM Parks_and_Recreation.employee_demographics dem
JOIN Parks_and_Recreation.employee_salary sal
  ON dem.employee_id = sal.employee_id
;