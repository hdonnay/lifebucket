CREATE EXTENSION hstore;
CREATE TABLE IF NOT EXISTS data ( time timestamp with time zone primary key, kv hstore );
