#! /bin/bash

exit 0


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

## replica setup

sudo -u postgres psql

show data_directory;

systemctl stop postgresql

rm -rf /var/lib/postgresql/14/main/*

pg_basebackup -h 10.0.0.56 \
-D /var/lib/postgresql/14/main/ \
-U repuser -vP -W

touch /var/lib/postgresql/14/main/standby.signal

vim /etc/postgresql/14/main/postgresql.conf

primary_conninfo = 'host=10.0.0.56 port=5432 user=repuser password=password application_name=r1'
primary_slot_name = 'replica_1_slot'

hot_standby = on
wal_level = replica
max_wal_senders = 2
max_replication_slots = 2
synchronous_commit = off

cd /var/lib/postgresql/14/main
sudo chown -R postgres:postgres .

cd /var/log/postgresql

systemctl start postgresql

less postgresql-14-main.log

