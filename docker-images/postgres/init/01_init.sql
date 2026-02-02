-- PostgreSQL Initialization Script
-- Executed automatically on first container startup

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search optimization

-- Set timezone to UTC
ALTER DATABASE k_user_management SET timezone TO 'UTC';

-- Performance tuning for development
-- Note: These are development settings, adjust for production
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = '0.9';
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = '100';
ALTER SYSTEM SET random_page_cost = '1.1';
ALTER SYSTEM SET effective_io_concurrency = '200';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET min_wal_size = '1GB';
ALTER SYSTEM SET max_wal_size = '4GB';

-- Connection pooling optimization
ALTER SYSTEM SET max_connections = '100';

-- Logging configuration for debugging
ALTER SYSTEM SET log_min_duration_statement = '500';  -- Log slow queries (>500ms)
ALTER SYSTEM SET log_connections = 'on';
ALTER SYSTEM SET log_disconnections = 'on';
ALTER SYSTEM SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';

-- Create read-only user for monitoring (optional)
CREATE USER k_readonly WITH PASSWORD 'readonly_dev';
GRANT CONNECT ON DATABASE k_user_management TO k_readonly;

-- Info message
DO $$
BEGIN
    RAISE NOTICE 'PostgreSQL initialized successfully for k-services';
    RAISE NOTICE 'Database: k_user_management';
    RAISE NOTICE 'Extensions enabled: uuid-ossp, pg_trgm';
    RAISE NOTICE 'Timezone: UTC';
    RAISE NOTICE 'Ready for Alembic migrations';
END $$;
