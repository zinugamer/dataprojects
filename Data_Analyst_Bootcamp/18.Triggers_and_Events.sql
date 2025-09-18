/*
    Triggers and Events
      - a block of code that executes automatically when
        an event takes place on a specific table.
	      - TRIGGER
          - EVENT

*/

SELECT *
FROM Parks_and_Recreation.employee_demographics;

-- (1) TRIGGER: 想要 每次update表employee_salary时 就把新插入的row也update进入demographics中
DELIMITER $$
CREATE TRIGGER employee_insert -- the name of the TRIGGER
    AFTER INSERT ON employee_salary -- the condition
    FOR EACH ROW
BEGIN -- the content of the execution
    INSERT INTO employee_demographics (employee_id, first_name, last_name)
    VALUES (NEW.employee_id, NEW.first_name, NEW.last_name);
END $$
DELIMITER ;

-- Try to insert a new record into employee_salary
INSERT INTO employee_salary (employee_id, first_name, last_name, occupation, salary, dept_id)
VALUES(13, 'Jean-Ralphio', 'Saperstein', 'Exntertainment 720 CEO', 1000000, NULL);
-- Check the results
SELECT *
FROM employee_salary;
SELECT *
FROM employee_demographics;


-- (2) EVENT
-- 初始化操作，确保我们后面创建的事件是最新的版本
DROP EVENT IF EXISTS delete_retirees;
-- 用 $$ 来告诉 MySQL：只有遇到 $$ 才算结束
DELIMITER $$
CREATE EVENT delete_retirees
ON SCHEDULE EVERY 30 SECOND -- 设定执行周期，这里是 每 30 秒自动运行一次
DO -- 开始定义 要执行的SQL语句
BEGIN
    DELETE 
    FROM employee_demographics
    WHERE age >= 60;
END $$
DELIMITER ;
-- Check the results
SELECT *
FROM employee_demographics;
-- 查看当前 MySQL 的 事件相关系统变量，event_scheduler事件调度器是否启用
SHOW VARIABLES LIKE 'event%';
-- SET GLOBAL event_scheduler = ON; 手动启用
