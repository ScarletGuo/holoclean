sudo -u postgres psql -c "copy (select datname from pg_database where datname like 'census_001_%') to stdout" | while read line; do
    echo "$line"
    sudo -u postgres dropdb -i "$line"
done
