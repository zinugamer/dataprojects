/*
    Temp Tables: tables that are only visible to that session
      - 一个session指的是同一次打开会话的时段，开一个新的窗口也算同一个session，但是
        关闭软件重新打开就是新的session
      - used for storing intermediate results for complex queries,
        also for manipulate data before insert it into a permanent table
*/

-- (1) Way #1 to create:
CREATE TEMPORARY TABLE temp_table (
first_name varchar(50),
last_name varchar(50),
favorite_movie varchar(100)
);

SELECT *
FROM temp_table;

INSERT INTO temp_table
VALUES('Alex', 'Freberg', 'Lord of the Rings: The Two Towers');

SELECT *
FROM temp_table;

-- (2)
SELECT *
FROM Parks_and_Recreation.employee_salary;

CREATE TEMPORARY TABLE salary_over_50k (
SELECT *
FROM Parks_and_Recreation.employee_salary
WHERE salary >= 50000
);

SELECT *
FROM salary_over_50k;

