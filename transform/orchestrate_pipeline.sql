-- -----------------------------------------------------------------------------
-- orchestrate_pipeline.sql
-- Master orchestrator: chains transformation scripts from the git stage
-- -----------------------------------------------------------------------------

EXECUTE IMMEDIATE FROM @DS5111_DB.WQP7QY.DS5111_GIT_STAGE/branches/lab09/transform/01_stg_youtube_transcripts.sql;
EXECUTE IMMEDIATE FROM @DS5111_DB.WQP7QY.DS5111_GIT_STAGE/branches/lab09/transform/02_dim_videos.sql;
EXECUTE IMMEDIATE FROM @DS5111_DB.WQP7QY.DS5111_GIT_STAGE/branches/lab09/transform/03_fct_entities.sql;
