-- OTT Streaming Data Pipeline
-- Athena Analytics Queries
-- Database: ott_streaming


-- =========================================================
-- Query 1: Basic title overview
-- =========================================================

SELECT
    content_type,
    COUNT(*) AS title_count
FROM titles
GROUP BY content_type
ORDER BY title_count DESC;


-- =========================================================
-- Query 2: Provider geographic coverage
-- =========================================================

SELECT
    p.provider_name,
    p.provider_type,
    COUNT(DISTINCT pr.region) AS region_count
FROM providers p
JOIN provider_regions pr
    ON p.provider_id = pr.provider_id
GROUP BY
    p.provider_name,
    p.provider_type
ORDER BY region_count DESC;


-- =========================================================
-- Query 3: Titles by release year
-- =========================================================

SELECT
    release_year,
    COUNT(*) AS title_count
FROM titles
WHERE release_year IS NOT NULL
GROUP BY release_year
ORDER BY
    title_count DESC,
    release_year DESC;


-- =========================================================
-- Query 4: Top 10 most popular titles
-- =========================================================

SELECT
    watchmode_id,
    title,
    release_year,
    content_type,
    popularity_percentile
FROM titles
WHERE popularity_percentile IS NOT NULL
ORDER BY
    popularity_percentile DESC,
    title ASC
LIMIT 10;


-- =========================================================
-- Query 5: Movies vs TV series distribution
-- =========================================================

SELECT
    content_type,
    COUNT(*) AS title_count,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM titles
GROUP BY content_type
ORDER BY title_count DESC;


-- =========================================================
-- Query 6: Average popularity by content type
-- =========================================================

SELECT
    content_type,
    COUNT(*) AS title_count,
    ROUND(AVG(popularity_percentile), 3) AS avg_popularity
FROM titles
WHERE popularity_percentile IS NOT NULL
GROUP BY content_type
ORDER BY avg_popularity DESC;


-- =========================================================
-- Query 7: Providers with the widest regional coverage
-- =========================================================

SELECT
    p.provider_name,
    p.provider_type,
    COUNT(DISTINCT pr.region) AS region_count
FROM providers p
JOIN provider_regions pr
    ON p.provider_id = pr.provider_id
GROUP BY
    p.provider_name,
    p.provider_type
ORDER BY region_count DESC
LIMIT 10;


-- =========================================================
-- Query 8: Regions with the most providers
-- =========================================================

SELECT
    pr.region,
    COUNT(DISTINCT pr.provider_id) AS provider_count
FROM provider_regions pr
GROUP BY pr.region
ORDER BY provider_count DESC
LIMIT 10;


-- =========================================================
-- Query 9: Titles by release year and content type
-- =========================================================

SELECT
    release_year,
    content_type,
    COUNT(*) AS title_count
FROM titles
WHERE release_year IS NOT NULL
GROUP BY
    release_year,
    content_type
ORDER BY
    release_year DESC,
    title_count DESC;