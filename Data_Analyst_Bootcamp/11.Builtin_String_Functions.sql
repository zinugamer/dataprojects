/*
    String Functions
      Built-in functions in MySQL
*/


-- (1) LENGTH
SELECT
  LENGTH('skyfall')
;

SELECT
  first_name, 
  LENGTH(first_name) as len_of_name
FROM
  Parks_and_Recreation.employee_demographics
ORDER BY 2 DESC
;

-- (2) UPPER & LOWER
SELECT UPPER('sky') as upper_case;

SELECT LOWER('SKY') as lower_case;

SELECT 
  first_name, 
  UPPER(first_name) as uppercase_name
FROM
  Parks_and_Recreation.employee_demographics
ORDER BY LENGTH(first_name)
;

-- (3) TRIM
SELECT TRIM('         sky          ');
SELECT LTRIM('         sky          ');
SELECT RTRIM('         sky          ');

-- (4) Substring methods
-- LEFT(col, num): SELECT num of characters from col
-- SUBSTRING(col, position_to_start, length)
SELECT
  first_name,
  LEFT(first_name, 4) as first_4_char_of_name
FROM Parks_and_Recreation.employee_demographics
;

SELECT
  first_name,
  LEFT(first_name, 4) as first_4_char_of_name,
  RIGHT(first_name, 4) as last_4_char_of_name,
  SUBSTRING(first_name, 3, 2) as substring_name
FROM Parks_and_Recreation.employee_demographics
;

WITH birth AS (
  SELECT
    first_name,
    birth_date,
    SUBSTRING(birth_date, 6, 2) as birth_month
  FROM Parks_and_Recreation.employee_demographics
)
SELECT 
  first_name,
  birth_date,
  CASE birth_month
    WHEN 01 THEN 'Jan'
    WHEN 02 THEN 'Feb'
    WHEN 03 THEN 'Mar'
    WHEN 04 THEN 'Apr'
    WHEN 05 THEN 'May'
    WHEN 06 THEN 'Jun'
    WHEN 07 THEN 'Jul'
    WHEN 08 THEN 'Aug'
    WHEN 09 THEN 'Sep'
    WHEN 10 THEN 'Oct'
    WHEN 11 THEN 'Nov'
    WHEN 12 THEN 'Dec'
    ELSE 'NA'
  END as birth_month
FROM birth;

-- (5) REPLACE
SELECT
  first_name,
  REPLACE(first_name, 'a', 'z') replaced_a_with_z
FROM Parks_and_Recreation.employee_demographics
;
-- (6) LOCATE(char, col_name)
SELECT
  first_name,
  LOCATE('An', first_name) as position_of_occurrance
FROM Parks_and_Recreation.employee_demographics
;

-- (7) CONCAT(col_name1, col_name2)
SELECT 
  first_name, 
  last_name,
  concat(first_name, ' ', last_name) as full_name
FROM
  Parks_and_Recreation.employee_demographics;