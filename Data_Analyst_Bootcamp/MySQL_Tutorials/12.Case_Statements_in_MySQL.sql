/*
    Case Statements

*/

-- (1) age
SELECT 
    first_name,
    last_name,
    age,
	CASE 
      WHEN age <= 30 THEN 'Young'
      WHEN age BETWEEN 31 AND 50 THEN 'Old'
	END AS Age_Bracket
FROM employee_demographics
;

-- (2) salary
-- Pay Increase and Bonus
-- < 50000 = 5%
-- > 50000 = 7%
-- Finance = 10% bonus
SELECT
    first_name,
    last_name,
    salary,
    CASE
      WHEN salary < 50000 THEN salary+salary*0.05
      WHEN salary > 50000 THEN salary+salary*0.07
      ELSE salary
	END AS New_Salary,
    CASE
      WHEN dept_id = 6 THEN salary * .10
	END AS bonus
FROM employee_salary
;