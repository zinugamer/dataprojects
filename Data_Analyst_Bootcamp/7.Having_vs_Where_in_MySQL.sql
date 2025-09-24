
/*
   HAVING vs. WHERE
   - 从聚合过的分组维度筛选
   - 从全量的表记录里筛选
   
   Error Code: 1111. Invalud Use of Group Function
     'GROUP BY'  only happens after 'SELECT'
     Note: 
     'GROUP BY' filters at the aggregate function level;
     'WHERE' clause filters at the row level
*/

-- (1) 
SELECT *
FROM 
    Parks_and_Recreation.employee_salary
;

-- (2)
SELECT 
  occupation, 
  AVG(salary)
FROM 
    Parks_and_Recreation.employee_salary
WHERE occupation LIKE '%manager%'
GROUP BY occupation
;

-- (3)
SELECT 
  occupation, 
  AVG(salary)
FROM 
    Parks_and_Recreation.employee_salary
WHERE occupation LIKE '%manager%'
GROUP BY occupation
HAVING AVG(salary) > 75000
;

-- (4) first names for each group, by GROUP_CONCAT(col ORDER BY col SEPARATOR )
SELECT 
    occupation,
    AVG(salary) AS avg_salary,
    GROUP_CONCAT(first_name ORDER BY first_name SEPARATOR ', ') AS employees
FROM 
    Parks_and_Recreation.employee_salary
GROUP BY 
    occupation
;
-- (5) 
SELECT 
    occupation,
    AVG(salary) AS avg_salary,
    GROUP_CONCAT(CONCAT(first_name, ' ', last_name) ORDER BY first_name SEPARATOR ', ') AS employees
FROM 
    Parks_and_Recreation.employee_salary
GROUP BY 
    occupation
;

