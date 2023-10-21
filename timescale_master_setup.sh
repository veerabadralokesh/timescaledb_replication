#! /bin/bash

exit 0

## https://docs.timescale.com/self-hosted/latest/install/installation-linux/


apt install gnupg postgresql-common apt-transport-https lsb-release wget

/usr/share/postgresql-common/pgdg/apt.postgresql.org.sh

echo "deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main" | sudo tee /etc/apt/sources.list.d/timescaledb.list

wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo apt-key add -

apt update

apt install timescaledb-2-postgresql-14

timescaledb-tune

apt-get update

apt-get install postgresql-client

systemctl restart postgresql

sudo -u postgres psql

\password postgres

\q

psql -U postgres -h localhost

CREATE database levylab;

\c levylab

CREATE EXTENSION IF NOT EXISTS timescaledb;

\dx

psql -U postgres -h localhost -d tsdb

CREATE TABLE public.llab_063 (
	"time" timestamptz NOT NULL,
	d000 float8 NULL,
	d001 float8 NULL,
	d002 float8 NULL
);
CREATE INDEX llab_063_time_idx ON public.llab_063 USING btree ("time" DESC);

# create trigger ts_insert_blocker before
# insert
#     on
#     public.llab_063 for each row execute function _timescaledb_internal.insert_blocker();

\d

\d+

SELECT create_hypertable('public.llab_063','time');

CREATE TABLE public.llab_063_index (
	"name" text NULL,
	units text NULL,
	"path" text NOT NULL,
	CONSTRAINT llab_063_index_name_key UNIQUE (name),
	CONSTRAINT llab_063_index_pkey PRIMARY KEY (path)
);

\dt

### setup replication user
# https://docs.timescale.com/self-hosted/latest/replication-and-ha/configure-replication/

CREATE ROLE repuser WITH REPLICATION PASSWORD 'password' LOGIN;

vim /etc/postgresql/14/main/postgresql.conf

listen_addresses = '*'
wal_level = replica
max_wal_senders = 2
max_replication_slots = 2
synchronous_commit = off

systemctl restart postgresql

psql -U postgres -h localhost -d levylab

SELECT * FROM pg_create_physical_replication_slot('replica_1_slot');

vim /etc/postgresql/14/main/pg_hba.conf

host    all             all             10.0.0.94/32            scram-sha-256
host    replication     all             10.0.0.94/32            scram-sha-256

systemctl restart postgresql

