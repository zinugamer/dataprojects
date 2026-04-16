
-- Exploratory Data Analysis

SELECT *
FROM world_layoffs.layoffs_staging2;

SELECT MAX(total_laid_off)
FROM world_layoffs.layoffs_staging2;

-- 发现取出来的数字不是最大的，说明数值变量的数据类型可能是字符串 VARCHAR，需要修改
ALTER TABLE world_layoffs.layoffs_staging2
MODIFY COLUMN total_laid_off DECIMAL(10,2),
MODIFY COLUMN percentage_laid_off DECIMAL(5,2),
MODIFY COLUMN funds_raised_millions DECIMAL(10,2)
;
-- 查看哪家公司，统计时段内的总裁员人数最多
SELECT company, SUM(total_laid_off)
FROM world_layoffs.layoffs_staging2
GROUP BY company 
ORDER BY 2 DESC;

-- 查看数据统计时段
SELECT 
	MIN(`date`) start_date, 
    MAX(`date`) end_date
FROM world_layoffs.layoffs_staging2;

-- 查看哪个行业，统计时段内的总裁员人数最多
SELECT industry, SUM(total_laid_off)
FROM world_layoffs.layoffs_staging2
GROUP BY industry
ORDER BY 2 DESC;

-- 查看哪一年，总裁员人数最多
SELECT 
	YEAR(`date`) `year`, 
    SUM(total_laid_off) 
FROM world_layoffs.layoffs_staging2
GROUP BY YEAR(`date`)
ORDER BY 2 DESC;

-- 查看统计时段内，哪一阶段的公司，总裁员人数最多
SELECT 
	stage, 
    SUM(total_laid_off) 
FROM world_layoffs.layoffs_staging2
GROUP BY stage
ORDER BY 2 DESC;

-- 滚动总裁员人数（月维度） Rolling Total Layoffs
SELECT 
	MONTH(`date`) `month`, 
    SUM(total_laid_off) 
FROM world_layoffs.layoffs_staging2
GROUP BY `month`
ORDER BY 1 ASC;

SELECT 
	SUBSTRING(`date`,6,2) `month`, 
    SUM(total_laid_off) 
FROM world_layoffs.layoffs_staging2
GROUP BY `month`
ORDER BY 1 ASC;

-- 滚动总裁员人数（年月维度） Rolling Total Layoffs
-- 滚动总数就是按时间顺序，累加，下一行都会更多
WITH Rolling_Total AS
(
SELECT 
	SUBSTRING(`date`,1,7) `month`, 
    SUM(total_laid_off) total_month_laid_off
FROM world_layoffs.layoffs_staging2
WHERE SUBSTRING(`date`,1,7) IS NOT NULL
GROUP BY `month`
ORDER BY 1 ASC
)
SELECT 
	`month`,
    total_month_laid_off,
    SUM(total_month_laid_off) OVER(ORDER BY `month`) AS rolling_total_laid_off
FROM Rolling_Total;

-- 公司年度总裁员人数
SELECT company, YEAR(`date`), SUM(total_laid_off)
FROM world_layoffs.layoffs_staging2
GROUP BY company, YEAR(`date`)
ORDER BY 1,2 DESC;

-- 每一年裁员人数最多的 Top5 Company（包括具体裁员人数、
-- 按年分类，从大到小排序裁员人数最多的公司，相同裁员人数的公司排名一致（DENSE_RANK)
WITH Company_Year (company,years,total_laid_off) AS
(
SELECT company, YEAR(`date`), SUM(total_laid_off)
FROM world_layoffs.layoffs_staging2
GROUP BY company, YEAR(`date`)
), Company_Year_Rank AS
(
SELECT *, 
	DENSE_RANK() OVER (PARTITION BY years ORDER BY total_laid_off DESC) AS ranking
FROM Company_Year
WHERE years IS NOT NULL
)
SELECT *
FROM Company_Year_Rank
WHERE ranking <= 5
;