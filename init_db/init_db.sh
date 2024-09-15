#!/bin/sh
set -e

echo "Creating database and tables..."

# Create the database if it doesn't exist
if ! psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='notes_db'" | grep -q 1; then
    echo "Database does not exist. Creating database..."
    psql -U postgres -c "CREATE DATABASE notes_db;"
else
    echo "Database already exists."
fi