/*
Cleaning Data in SQL Queries
*/
-- ----------------------------------------------------------------------

-- Explore the table
SELECT *
FROM PortfolioProject.NashvilleHousing;

-- (1) Checking keys
SHOW KEYS FROM PortfolioProject.NashvilleHousing;
-- (2) Checking if the col 'UniqueID' has duplicate values
SELECT UniqueID, COUNT(*) 
FROM NashvilleHousing 
GROUP BY UniqueID 
HAVING COUNT(*) > 1;
-- (3) Adding a primary key for this table
ALTER TABLE PortfolioProject.NashvilleHousing
ADD COLUMN RowID INT AUTO_INCREMENT PRIMARY KEY;

-- ----------------------------------------------------------------------

-- 1 Standardize Data Format for date col

-- (1) Looking at the current date col
SELECT 
	SaleDate, 
    STR_TO_DATE(SaleDate,'%M %e, %Y') AS date
FROM PortfolioProject.NashvilleHousing;

-- (2) Save parsed date col by creating a new col in dataframe/table
/*
Step1 Create a new col with NULLs
Step2 Populate the new col with parsed dates
*/
ALTER TABLE PortfolioProject.NashvilleHousing
ADD COLUMN SaleDateConverted date; 

UPDATE NashvilleHousing
SET SaleDateConverted = STR_TO_DATE(SaleDate,'%M %e, %Y')
WHERE UniqueID >0;
-- ----------------------------------------------------------------------

-- 2 Address Data

-- 2.1 Handling Missing Values
-- (1) Check Missing Values: Check if there exists NULL or empty values
SELECT ParcelID, PropertyAddress
FROM PortfolioProject.NashvilleHousing
WHERE ParcelID IS NULL OR ParcelID = '';

SELECT ParcelID, PropertyAddress
FROM PortfolioProject.NashvilleHousing
WHERE PropertyAddress IS NULL OR PropertyAddress = ''; -- there eixts empty values

-- (2) Fill empty cells using correct values
-- firstly check what values we can use by SELF JOIN, PropertyAddress can be found from other records for the same ParcelID
-- check if exists
SELECT ParcelID, COUNT(*)
FROM PortfolioProject.NashvilleHousing
GROUP BY ParcelID;

SELECT
	a.ParcelID, a.PropertyAddress,
    b.ParcelID, b.PropertyAddress
FROM
  PortfolioProject.NashvilleHousing AS a
  JOIN PortfolioProject.NashvilleHousing AS b
  ON a.ParcelID = b.ParcelID
  AND a.UniqueID <> b.UniqueID -- NOT EQUAL SIGN '<>'
WHERE a.PropertyAddress = '';

-- (3) For the same ParcelID: If a.PropertyAddress IS empty, fill in with values of b.PropertyAddress
UPDATE PortfolioProject.NashvilleHousing AS a
  JOIN PortfolioProject.NashvilleHousing AS b
  ON a.ParcelID = b.ParcelID
  AND a.UniqueID <> b.UniqueID
SET a.PropertyAddress = b.PropertyAddress
WHERE a.PropertyAddress = '' AND a.RowID > 0;

-- Check if empty cells still exist
SELECT ParcelID, PropertyAddress
FROM PortfolioProject.NashvilleHousing
WHERE PropertyAddress IS NULL OR PropertyAddress = ''
ORDER BY ParcelID; -- empty fixed!!!

-- ----------------------------------------------------------------------

-- 2.2 
-- Breaking out Address into Individual Columns (Address, City, State)

-- (1) Looking at the Address column
SELECT PropertyAddress
FROM PortfolioProject.NashvilleHousing;

-- (2) Breaking out the add by delimiter ','
SELECT 
	TRIM(SUBSTRING_INDEX(PropertyAddress, ',', 1)) AS Address,
    TRIM(SUBSTRING_INDEX(PropertyAddress, ',', -1)) AS City
FROM PortfolioProject.NashvilleHousing;

-- (3) Updating the splitted Address cols in the table
ALTER TABLE PortfolioProject.NashvilleHousing
ADD COLUMN PropertySplitAddress VARCHAR(255);

UPDATE NashvilleHousing
SET PropertySplitAddress = TRIM(SUBSTRING_INDEX(PropertyAddress, ',', 1))
WHERE RowID > 0; 


ALTER TABLE PortfolioProject.NashvilleHousing
ADD COLUMN PropertySplitCity VARCHAR(255);

UPDATE NashvilleHousing
SET PropertySplitCity = TRIM(SUBSTRING_INDEX(PropertyAddress, ',', -1))
WHERE RowID > 0; 

-- (4) Simple method for the col 'OwnerAddress'
SELECT OwnerAddress
FROM PortfolioProject.NashvilleHousing;

SELECT
    TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(OwnerAddress, ',', 3), ',', -1)) AS Part3,
    TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(OwnerAddress, ',', 2), ',', -1)) AS Part2,
    TRIM(SUBSTRING_INDEX(OwnerAddress, ',', 1)) AS Part1
FROM 
  PortfolioProject.NashvilleHousing;


ALTER TABLE PortfolioProject.NashvilleHousing
ADD COLUMN OwnerSplitAddress VARCHAR(255);
UPDATE NashvilleHousing
SET OwnerSplitAddress = TRIM(SUBSTRING_INDEX(OwnerAddress, ',', 1))
WHERE RowID > 0; 

ALTER TABLE PortfolioProject.NashvilleHousing
ADD COLUMN OwnerSplitCity VARCHAR(255);
UPDATE NashvilleHousing
SET OwnerSplitCity = TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(OwnerAddress, ',', 2), ',', -1))
WHERE RowID > 0; 

ALTER TABLE PortfolioProject.NashvilleHousing
ADD COLUMN OwnerSplitState VARCHAR(255);
UPDATE NashvilleHousing
SET OwnerSplitState = TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(OwnerAddress, ',', 3), ',', -1))
WHERE RowID > 0; 

-- ----------------------------------------------------------------------

-- 2.3

-- Change Y and N to 'Yes' and 'No' in 'Sold as Vacant' field
SELECT SoldAsVacant, COUNT(SoldAsVacant)
FROM PortfolioProject.NashvilleHousing
GROUP BY SoldAsVacant
ORDER BY COUNT(SoldAsVacant) DESC;

SELECT 
    SoldAsVacant, 
    CASE WHEN SoldAsVacant = 'Y' THEN 'Yes'
         WHEN SoldAsVacant = 'N' THEN 'No'
         ELSE SoldAsVacant
    END
FROM PortfolioProject.NashvilleHousing
GROUP BY SoldAsVacant
ORDER BY COUNT(SoldAsVacant) DESC;



UPDATE PortfolioProject.NashvilleHousing
SET SoldAsVacant = 'YES'
WHERE SoldAsVacant = 'Y' AND RowID > 0;

UPDATE PortfolioProject.NashvilleHousing
SET SoldAsVacant = 'NO'
WHERE SoldAsVacant = 'N' AND RowID > 0;
/* Set multiple values at once
UPDATE PortfolioProject.NashvilleHousing
SET SoldAsVacant = 
    CASE 
        WHEN SoldAsVacant = 'Y' THEN 'Yes'
        WHEN SoldAsVacant = 'N' THEN 'No'
        ELSE SoldAsVacant
    END;
*/
-- ----------------------------------------------------------------------


-- 2.4 grouping the data based on a combination, assigns a number to each row, starting at 1, Inside each partition, rows are ordered by UniqueID

WITH RowNumCTE AS (
SELECT *,
    ROW_NUMBER() OVER (
    PARTITION BY ParcelID,
                 PropertyAddress,
				 SalePrice,
                 SaleDate,
				 LegalReference
				 ORDER BY
                   UniqueID) AS row_num
FROM
  PortfolioProject.NashvilleHousing
ORDER BY ParcelID
)

/*
SELECT *
FROM RowNumCTE
WHERE row_num > 1
ORDER BY PropertyAddress;
*/

-- Delete records with row_num > 1 only, by self inner join
DELETE a
FROM PortfolioProject.NashvilleHousing AS a
  JOIN RowNumCTE AS b
    ON a.UniqueID = b.UniqueID
WHERE b.row_num > 1 AND a.RowID > 0;


-- Delete some other unuseable columns

SELECT *
FROM PortfolioProject.NashvilleHousing;

ALTER TABLE PortfolioProject.NashvilleHousing;

ALTER TABLE PortfolioProject.NashvilleHousing
DROP COLUMN SaleDate;