#!/bin/bash

# Universal Database Restore Script
# Automatically detects backup type and restores to running database

DB_NAME="{KAVIA_DB_NAME}"
DB_USER="{KAVIA_DB_USER}"
DB_PASSWORD="{KAVIA_DB_PASSWORD}"
DB_PORT="{KAVIA_DB_PORT}"

# SQLite restore
if [ -f "database_backup.db" ] && [ -f "${DB_NAME}" ]; then
    echo "Restoring SQLite database from backup..."
    cp "database_backup.db" "${DB_NAME}"
    echo "✓ Database restored successfully"
    exit 0
fi

# PostgreSQL/MySQL restore from SQL file
if [ -f "database_backup.sql" ]; then
    # Try PostgreSQL
    PG_VERSION=$(ls /usr/lib/postgresql/ 2>/dev/null | head -1)
    if [ -n "$PG_VERSION" ]; then
        PG_BIN="/usr/lib/postgresql/${PG_VERSION}/bin"
        if sudo -u postgres ${PG_BIN}/pg_isready -p ${DB_PORT} > /dev/null 2>&1; then
            echo "Restoring PostgreSQL database from backup..."
            PGPASSWORD="${DB_PASSWORD}" ${PG_BIN}/psql \
                -h localhost -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} \
                < database_backup.sql 2>/dev/null
            echo "✓ Database restored successfully"
            exit 0
        fi
    fi
    
    # Try MySQL - Fixed to use correct port and TCP connection
    # Check if MySQL is running on the specified port
    if mysqladmin ping -h localhost -P ${DB_PORT} --silent 2>/dev/null || \
       sudo mysqladmin ping --socket=/var/run/mysqld/mysqld.sock --silent 2>/dev/null; then
        echo "Restoring MySQL database from backup..."
        
        # First try with TCP connection on specified port (for Docker or custom port setups)
        if mysql -h localhost -P ${DB_PORT} -u ${DB_USER} -p${DB_PASSWORD} \
            -e "SELECT 1" >/dev/null 2>&1; then
            mysql -h localhost -P ${DB_PORT} -u ${DB_USER} -p${DB_PASSWORD} \
                < database_backup.sql
            echo "✓ Database restored successfully (via TCP port ${DB_PORT})"
            exit 0
        fi
        
        # Fallback to root user with TCP if appuser doesn't work
        if mysql -h localhost -P ${DB_PORT} -u root -p${DB_PASSWORD} \
            -e "SELECT 1" >/dev/null 2>&1; then
            mysql -h localhost -P ${DB_PORT} -u root -p${DB_PASSWORD} \
                < database_backup.sql
            echo "✓ Database restored successfully (via TCP port ${DB_PORT} as root)"
            exit 0
        fi
        
        # Final fallback to socket connection for standard MySQL installations
        if sudo mysql --socket=/var/run/mysqld/mysqld.sock \
            -u root -p${DB_PASSWORD} -e "SELECT 1" >/dev/null 2>&1; then
            sudo mysql --socket=/var/run/mysqld/mysqld.sock \
                -u root -p${DB_PASSWORD} < database_backup.sql
            echo "✓ Database restored successfully (via socket)"
            exit 0
        fi
        
        # Try without password for local root
        if sudo mysql --socket=/var/run/mysqld/mysqld.sock \
            -u root -e "SELECT 1" >/dev/null 2>&1; then
            sudo mysql --socket=/var/run/mysqld/mysqld.sock \
                -u root < database_backup.sql
            echo "✓ Database restored successfully (via socket, no password)"
            exit 0
        fi
        
        echo "⚠ MySQL is running but authentication failed"
        echo "  Please check your credentials"
        exit 1
    fi
fi

# MongoDB restore from archive
if [ -f "database_backup.archive" ]; then
    if mongosh --port ${DB_PORT} --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        echo "Restoring MongoDB database from backup..."
        mongorestore --port ${DB_PORT} --archive=database_backup.archive \
            --drop --quiet
        echo "✓ Database restored successfully"
        exit 0
    fi
fi

echo "ℹ No backup found or database not running"
echo "  Starting with fresh database"
echo ""
echo "Backup files checked:"
echo "  - database_backup.db (SQLite)"
echo "  - database_backup.sql (PostgreSQL/MySQL)"  
echo "  - database_backup.archive (MongoDB)"
exit 0
