/*
    Data Cleaning Project
     - 背景：company layoffs 公司裁员情况分析
     - 操作 Steps:
       1. Remove Dupicates删除重复记录
       2. Standardize the Data数据标准化
       3. Null Values or blank values处理空值
       4. Remove Any Columns删除非关键指标/无关属性
*/

-- Create table for raw data
DROP TABLE IF EXISTS world_layoffs.layoffs;

CREATE TABLE world_layoffs.layoffs (
    company VARCHAR(255),
    location VARCHAR(255),
    industry VARCHAR(255),
    total_laid_off VARCHAR(255),
    percentage_laid_off VARCHAR(255),
    `date` VARCHAR(255),
    stage VARCHAR(255),
    country VARCHAR(255),
    funds_raised_millions VARCHAR(255)
);

-- Import data by Data Import Wizard OR Python code (better since handling NaNs/Nulls)

SELECT *
FROM world_layoffs.layoffs
;

-- Create a staging table with same column names as raw data table
DROP TABLE IF EXISTS world_layoffs.layoffs_staging;
CREATE TABLE world_layoffs.layoffs_staging
LIKE world_layoffs.layoffs
;

SELECT *
FROM world_layoffs.layoffs_staging
;

-- Insert data by copying from layoffs raw data
INSERT world_layoffs.layoffs_staging
SELECT *
FROM world_layoffs.layoffs
;

SELECT *
FROM world_layoffs.layoffs_staging
;

-- Data Cleaning 开始数据清洗
-- (1) Remove Duplicates by creating CTE with Partitions (row numbers for each group)

WITH duplicate_cte AS
(
SELECT *,
ROW_NUMBER() OVER(
PARTITION BY company, location, industry, total_laid_off, percentage_laid_off, `date`, stage, country, funds_raised_millions) AS row_num
FROM world_layoffs.layoffs_staging
)
-- Show duplicated rows
SELECT *
FROM duplicate_cte
WHERE row_num > 1
;

-- double check检查当前分组方式是否的确是完全一致的记录
SELECT *
FROM world_layoffs.layoffs_staging
WHERE company = 'Oda'
;

-- 右键目标 table 下拉菜单'Copy to Clipboard - Create Statement'
DROP TABLE IF EXISTS world_layoffs.layoffs_staging2;
CREATE TABLE `world_layoffs`.`layoffs_staging2` (
  `company` varchar(255) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `industry` varchar(255) DEFAULT NULL,
  `total_laid_off` varchar(255) DEFAULT NULL,
  `percentage_laid_off` varchar(255) DEFAULT NULL,
  `date` varchar(255) DEFAULT NULL,
  `stage` varchar(255) DEFAULT NULL,
  `country` varchar(255) DEFAULT NULL,
  `funds_raised_millions` varchar(255) DEFAULT NULL,
  `row_num` INT DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SELECT *
FROM world_layoffs.layoffs_staging2
;

INSERT INTO world_layoffs.layoffs_staging2
SELECT *,
ROW_NUMBER() OVER(
PARTITION BY company, location, industry, total_laid_off, percentage_laid_off, `date`, stage, country, funds_raised_millions) AS row_num
FROM world_layoffs.layoffs_staging
;

SELECT *
FROM world_layoffs.layoffs_staging2
;
SELECT *
FROM world_layoffs.layoffs_staging2
WHERE row_num > 1
;

-- 临时关闭安全模式，删除重复行之后，恢复安全模式
SET SQL_SAFE_UPDATES = 0;

DELETE FROM world_layoffs.layoffs_staging2 WHERE row_num > 1;

SET SQL_SAFE_UPDATES = 1;  -- 可选：执行完后再打开安全模式

SELECT *
FROM world_layoffs.layoffs_staging2
WHERE row_num > 1
;

-- (2) Standardizing Data: Find issues in yr data and then fixing it
-- company col
SELECT *
FROM world_layoffs.layoffs_staging2
;

SELECT company, TRIM(company)
FROM world_layoffs.layoffs_staging2;

SET SQL_SAFE_UPDATES = 0;
UPDATE world_layoffs.layoffs_staging2
SET company = TRIM(company);
SET SQL_SAFE_UPDATES = 1;

SELECT company, TRIM(company)
FROM world_layoffs.layoffs_staging2;

-- industry col: find similar cols like Crypto, Crypto Currency, CryptoCurrency
SELECT DISTINCT industry
FROM world_layoffs.layoffs_staging2
ORDER BY 1
;

SELECT DISTINCT industry
FROM world_layoffs.layoffs_staging2
WHERE industry LIKE '%Crypto%'
;

SET SQL_SAFE_UPDATES = 0;
UPDATE world_layoffs.layoffs_staging2
SET industry = 'Crypto' WHERE industry LIKE '%Crypto%';
SET SQL_SAFE_UPDATES = 1;

SELECT DISTINCT industry
FROM world_layoffs.layoffs_staging2
ORDER BY 1
;

-- country col: United States & United States.

-- similar records for the same meaning
SELECT DISTINCT country
FROM world_layoffs.layoffs_staging2
ORDER BY 1
;

SELECT DISTINCT country
FROM world_layoffs.layoffs_staging2
WHERE country LIKE '%United States%'
;

SET SQL_SAFE_UPDATES = 0;
UPDATE world_layoffs.layoffs_staging2
SET country = 'United States' WHERE country LIKE '%United States%';
SET SQL_SAFE_UPDATES = 1;

SELECT DISTINCT country
FROM world_layoffs.layoffs_staging2
WHERE country LIKE '%United States%'
;

-- method#2 TRIM(TRAILING '.' FROM country)
SELECT DISTINCT country, TRIM(TRAILING '.' FROM country)
FROM world_layoffs.layoffs_staging2
ORDER BY 1
;

-- date col: IMPORTANT! if we wanna a time series visualizations, then need to clean the date col well
-- Formatting the date col, to the correct data type
SELECT 
  `date`,
  STR_TO_DATE(`date`, '%m/%d/%Y') AS revised_date
FROM world_layoffs.layoffs_staging2
;

SET SQL_SAFE_UPDATES = 0;
UPDATE world_layoffs.layoffs_staging2
SET `date` = STR_TO_DATE(`date`, '%m/%d/%Y');
SET SQL_SAFE_UPDATES = 1
;

SELECT 
  `date`
FROM world_layoffs.layoffs_staging2
ORDER BY 1 -- dates ordered properly as chronological values instead of strings
;
-- Change the column type
ALTER TABLE world_layoffs.layoffs_staging2
MODIFY COLUMN `date` date
;

-- (3) Null Values or blank values
-- total_laid_off
SELECT *
FROM world_layoffs.layoffs_staging2
WHERE total_laid_off IS NULL
AND percentage_laid_off IS NULL
;

-- industry
SELECT *
FROM world_layoffs.layoffs_staging2
WHERE industry IS NULL
OR industry = ''
;


SELECT *
FROM world_layoffs.layoffs_staging2
WHERE company = 'Airbnb'
;

SELECT *
FROM world_layoffs.layoffs_staging2 t1
JOIN world_layoffs.layoffs_staging2 t2
  ON t1.company = t2.company
WHERE t1.industry IS NULL
AND t2.industry IS NOT NULL
;

-- 把blanks修改为NULL
SET SQL_SAFE_UPDATES = 0;
UPDATE world_layoffs.layoffs_staging2
SET industry = NULL
WHERE industry = '';
SET SQL_SAFE_UPDATES = 1;


-- Populate nulls 用存在记录的填补空缺
SET SQL_SAFE_UPDATES = 0;
UPDATE world_layoffs.layoffs_staging2 t1
JOIN world_layoffs.layoffs_staging2 t2
  ON t1.company = t2.company
SET t1.industry = t2.industry
WHERE t1.industry IS NULL
AND t2.industry IS NOT NULL
;
SET SQL_SAFE_UPDATES = 1;

-- 检查是否修改成功（是否还存在一个为空一个不为空的情况）
SELECT *
FROM world_layoffs.layoffs_staging2 t1
JOIN world_layoffs.layoffs_staging2 t2
  ON t1.company = t2.company
WHERE t1.industry IS NULL
AND t2.industry IS NOT NULL
;

-- 检查是否还存在空值（没有多条记录，无法交叉填充的记录）
SELECT *
FROM world_layoffs.layoffs_staging2
WHERE industry IS NULL
OR industry = ''
;

-- 进一步看公司Bally's
SELECT *
FROM world_layoffs.layoffs_staging2
WHERE company LIKE 'Bally%'
;

-- (4) Remove Any Columns
-- 先观察关键指标和此指标的因子指标是不是都为空
SELECT *
FROM world_layoffs.layoffs_staging2
WHERE total_laid_off IS NULL
AND percentage_laid_off IS NULL
;

-- 公司总人数、裁员总数、裁员占比都为空，则无法计算想要的裁员占比，那么这个记录就是无效的
SET SQL_SAFE_UPDATES = 0;
DELETE
FROM world_layoffs.layoffs_staging2
WHERE total_laid_off IS NULL
AND percentage_laid_off IS NULL
;
SET SQL_SAFE_UPDATES = 1;

SELECT *
FROM world_layoffs.layoffs_staging2
WHERE total_laid_off IS NULL
AND percentage_laid_off IS NULL
;

SELECT *
FROM world_layoffs.layoffs_staging2
;

-- 去除一开始增加的column field列字段 'row_num'
SET SQL_SAFE_UPDATES = 0;
ALTER TABLE world_layoffs.layoffs_staging2
DROP COLUMN row_num
;
SET SQL_SAFE_UPDATES = 1;

