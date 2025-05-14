SELECT *
FROM PortfolioProject.coviddeaths
WHERE continent IS NOT NULL
  AND TRIM(continent) != ''
ORDER BY 3,4;


SELECT location, date, total_cases, new_cases, total_deaths, population
FROM PortfolioProject.coviddeaths
WHERE continent IS NOT NULL
  AND TRIM(continent) != ''
ORDER BY 1,2;

-- Looking at Total Cases vs. Total Deaths
-- Shows what percentage of Infected Cases were dead
SELECT location, date, total_cases, total_deaths, (total_deaths/total_cases)*100 AS DeathPercentage
FROM PortfolioProject.coviddeaths
WHERE location like '%state%' 
  AND continent IS NOT NULL 
  AND TRIM(continent) != ''
ORDER BY 1,2;

-- Looking at Total Cases vs. Population
-- Shows what percentage of population got Covid
SELECT location, date, population, total_cases, (total_cases/population)*100 AS CovidPercentage
FROM PortfolioProject.coviddeaths
WHERE location like '%state%' 
  AND continent IS NOT NULL
  AND TRIM(continent) != ''
ORDER BY 1,2;

-- Looking at Countries with Highest Infection Rate compared to Population
SELECT location, population, MAX(total_cases) AS HighestInfectionCount, MAX(total_cases/population)*100 AS PercentagePopulationInfected
FROM PortfolioProject.coviddeaths
-- WHERE location like '%state%'
WHERE continent IS NOT NULL
  AND TRIM(continent) != ''
GROUP BY location, population
ORDER BY PercentagePopulationInfected DESC;

-- Showing Countries with Highest Death Count per Population
SELECT 
    location, 
    MAX(CAST(total_deaths AS UNSIGNED)) AS TotalDeathCount,
    population,
    MAX(CAST(total_deaths AS UNSIGNED)) / population AS DeathsPerPopulation
FROM PortfolioProject.coviddeaths
WHERE population IS NOT NULL
  AND total_deaths IS NOT NULL
  AND continent IS NOT NULL
  AND TRIM(continent) != ''
-- WHERE location like '%state%'
GROUP BY location, population
ORDER BY DeathsPerPopulation DESC;

-- Showing Highest Death Count By Countries
SELECT 
    location, 
    MAX(CAST(total_deaths AS UNSIGNED)) AS TotalDeathCount
FROM PortfolioProject.coviddeaths
WHERE continent IS NOT NULL
  AND TRIM(continent) != ''
-- WHERE location like '%state%'
GROUP BY location
ORDER BY TotalDeathCount DESC;

-- Showing Highest Death Count By Continents
SELECT 
    continent, 
    MAX(CAST(total_deaths AS UNSIGNED)) AS TotalDeathCount
FROM PortfolioProject.coviddeaths
WHERE continent IS NOT NULL
  AND TRIM(continent) != ''
-- WHERE location like '%state%'
GROUP BY continent
ORDER BY TotalDeathCount DESC;

-- Showing Global Increments (New Cases Daily)
SELECT 
    STR_TO_DATE(date, '%Y/%c/%e') AS parsed_date,
    SUM(new_cases) AS total_cases,
    SUM(CAST(new_deaths AS UNSIGNED)) AS total_deaths,
    SUM(CAST(new_deaths AS UNSIGNED))/SUM(new_cases)*100 AS DeathPercentage
FROM PortfolioProject.coviddeaths
WHERE continent IS NOT NULL
  AND TRIM(continent) != ''
GROUP BY str_to_date(date, '%Y/%c/%e')
ORDER BY 1,2;
    
-- Showing Global Increments (New Cases Daily)
SELECT 
    SUM(new_cases) AS total_cases,
    SUM(new_deaths) AS total_deaths,
    SUM(new_deaths)/SUM(new_cases) *100 AS DeathPercentage
FROM PortfolioProject.coviddeaths
WHERE continent IS NOT NULL
  AND TRIM(continent) != '';
  
-- Vaccinations Table
SELECT *
FROM PortfolioProject.covidvaccinations;

-- Looking at Total Population vs. Vaccinations, accumulated amount by country
SELECT 
  dea.continent, 
  dea.location, 
  str_to_date(dea.date, '%Y/%c/%e') AS date, 
  dea.population, 
  vac.new_vaccinations,
  SUM(CONVERT(vac.new_vaccinations, UNSIGNED)) OVER (PARTITION BY dea.location) AS cumulative_vacc
FROM PortfolioProject.coviddeaths dea
JOIN PortfolioProject.covidvaccinations vac
    ON dea.location = vac.location
      AND dea.date = vac.date
WHERE dea.continent IS NOT NULL
  AND vac.new_vaccinations REGEXP '^[0-9]+$'
ORDER BY location, date;

-- Looking at Total Population vs. Vaccinations, accumulated amount by date
SELECT 
  dea.continent, 
  dea.location, 
  str_to_date(dea.date, '%Y/%c/%e') AS date, 
  dea.population, 
  vac.new_vaccinations,
  SUM(CONVERT(vac.new_vaccinations, UNSIGNED)) 
    OVER (PARTITION BY dea.location ORDER BY str_to_date(dea.date, '%Y/%c/%e')) AS RollingPeopleVaccinated
FROM PortfolioProject.coviddeaths dea
JOIN PortfolioProject.covidvaccinations vac
    ON dea.location = vac.location
      AND dea.date = vac.date
WHERE dea.continent IS NOT NULL
ORDER BY location, date;

-- Use CTE if we need to use newly-defined features in select
WITH PopvsVac (continent, location, date, population, new_vaccinations, RollingPeopleVaccinated)
AS
(
SELECT 
  dea.continent, 
  dea.location, 
  str_to_date(dea.date, '%Y/%c/%e') AS date, 
  dea.population, 
  vac.new_vaccinations,
  SUM(CONVERT(vac.new_vaccinations, UNSIGNED)) 
    OVER (PARTITION BY dea.location ORDER BY str_to_date(dea.date, '%Y/%c/%e')) AS RollingPeopleVaccinated
FROM PortfolioProject.coviddeaths dea
JOIN PortfolioProject.covidvaccinations vac
    ON dea.location = vac.location
      AND dea.date = vac.date
WHERE dea.continent IS NOT NULL
ORDER BY location, date
)

SELECT *, (RollingPeopleVaccinated/Population)*100 AS PercentagePopulationVaccinated
FROM PopvsVac;


-- TEMP TABLE

DROP TEMPORARY TABLE IF EXISTS PercentagePopulationVaccinated;
CREATE TEMPORARY TABLE PercentagePopulationVaccinated
(
continent nvarchar(255),
location nvarchar(255),
date datetime,
population numeric,
new_vaccinations numeric,
RollingPeopleVaccinated numeric
);
INSERT INTO PercentagePopulationVaccinated
SELECT 
  dea.continent, 
  dea.location, 
  str_to_date(dea.date, '%Y/%c/%e') AS date, 
  dea.population, 
  CASE
	  WHEN vac.new_vaccinations REGEXP '^[0-9]+$'
      THEN CONVERT(vac.new_vaccinations, UNSIGNED)
      ELSE 0
  END AS new_vaccinations,
  SUM(
    CASE
	  WHEN vac.new_vaccinations REGEXP '^[0-9]+$'
      THEN CONVERT(vac.new_vaccinations, UNSIGNED)
      ELSE 0
	END
    ) OVER (PARTITION BY dea.location ORDER BY str_to_date(dea.date, '%Y/%c/%e')) AS RollingPeopleVaccinated
FROM PortfolioProject.coviddeaths dea
JOIN PortfolioProject.covidvaccinations vac
    ON dea.location = vac.location
      AND dea.date = vac.date
WHERE dea.continent IS NOT NULL
ORDER BY location, date;

SELECT *, (RollingPeopleVaccinated/Population)*100 AS PercentagePopulationVaccinated
FROM PercentagePopulationVaccinated;

-- Create a View

DROP VIEW IF EXISTS vw_customer_orders;

CREATE VIEW vw_customer_orders AS
SELECT 
  dea.continent, 
  dea.location, 
  str_to_date(dea.date, '%Y/%c/%e') AS date, 
  dea.population, 
  vac.new_vaccinations,
  SUM(CONVERT(vac.new_vaccinations, UNSIGNED)) 
    OVER (PARTITION BY dea.location ORDER BY str_to_date(dea.date, '%Y/%c/%e')) AS RollingPeopleVaccinated
FROM PortfolioProject.coviddeaths dea
JOIN PortfolioProject.covidvaccinations vac
    ON dea.location = vac.location
      AND dea.date = vac.date
WHERE dea.continent IS NOT NULL
ORDER BY location, date;

SELECT * FROM vw_customer_orders;
