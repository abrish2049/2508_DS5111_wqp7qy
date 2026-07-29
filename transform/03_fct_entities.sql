-- -----------------------------------------------------------------------------
-- 03_fct_entities.sql
-- Fact tables: unnest VARIANT arrays via LATERAL FLATTEN
-- -----------------------------------------------------------------------------

-- Flatten tech_terms array into relational fact rows
CREATE OR REPLACE TABLE FCT_TECH_TERMS AS
SELECT
    VIDEO_ID,
    f.value::STRING AS TECH_TERM,
    INSERTED_AT     AS PROCESSED_AT
FROM STG_YOUTUBE_TRANSCRIPTS,
LATERAL FLATTEN(input => TECH_TERMS_ARRAY) f;

-- Flatten book_names array into relational fact rows
CREATE OR REPLACE TABLE FCT_BOOK_MENTIONS AS
SELECT
    VIDEO_ID,
    f.value::STRING AS BOOK_NAME,
    INSERTED_AT     AS PROCESSED_AT
FROM STG_YOUTUBE_TRANSCRIPTS,
LATERAL FLATTEN(input => BOOK_NAMES_ARRAY) f;
