-- -----------------------------------------------------------------------------
-- 01_stg_youtube_transcripts.sql
-- Staging view: parse JSON_PAYLOAD VARIANT into typed relational columns
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW STG_YOUTUBE_TRANSCRIPTS AS
SELECT
    JSON_PAYLOAD:video_id::STRING       AS VIDEO_ID,
    JSON_PAYLOAD:cleaned_text::STRING   AS CLEANED_TEXT,
    JSON_PAYLOAD:tech_terms             AS TECH_TERMS_ARRAY,
    JSON_PAYLOAD:book_names             AS BOOK_NAMES_ARRAY,
    INSERTED_AT
FROM DS5111_DB.WQP7QY.RAW_TRANSCRIPTS;
