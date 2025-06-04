#!/bin/bash

# Fixed MySQL startup script for MySQL 8.0 authentication
DB_NAME="{KAVIA_DB_NAME}"
DB_USER="{KAVIA_DB_USER}"
DB_PASSWORD="{KAVIA_DB_PASSWORD}"
DB_PORT="{KAVIA_DB_PORT}"

# Initialize MySQL data directory if it doesn't exist
if [ ! -d "/var/lib/mysql/mysql" ]; then
    echo "Initializing MySQL..."
    sudo mysqld --initialize-insecure --user=mysql --datadir=/var/lib/mysql
fi

# Start MySQL server in background using sudo
echo "Starting MySQL server..."
sudo mysqld --user=mysql --datadir=/var/lib/mysql --socket=/var/run/mysqld/mysqld.sock --pid-file=/var/run/mysqld/mysqld.pid --port=${DB_PORT} &

# Wait for MySQL to be ready
echo "Waiting for MySQL to start..."
sleep 5

# Check if MySQL is running using socket
for i in {1..15}; do
    if sudo mysqladmin ping --socket=/var/run/mysqld/mysqld.sock --silent 2>/dev/null; then
        echo "MySQL is ready!"
        break
    fi
    echo "Waiting... ($i/15)"
    sleep 2
done

# Configure database and user - Fix MySQL 8.0 authentication
echo "Setting up database and fixing authentication..."
sudo mysql --socket=/var/run/mysqld/mysqld.sock << EOF
-- Fix root user authentication for MySQL 8.0
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${DB_PASSWORD}';

-- Create database
CREATE DATABASE IF NOT EXISTS ${DB_NAME};

-- Create a new user for remote connections
CREATE USER IF NOT EXISTS 'appuser'@'%' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO 'appuser'@'%';

-- Grant privileges to root
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO 'root'@'localhost';

FLUSH PRIVILEGES;
EOF

# Save connection command to a file
echo "mysql -u ${DB_USER} -p${DB_PASSWORD} -h localhost -P ${DB_PORT} ${DB_NAME}" > db_connection.txt
echo "Connection command saved to db_connection.txt"

echo "MySQL setup complete!"
echo "Database: ${DB_NAME}"
echo "Root user: root (password: ${DB_PASSWORD})"
echo "App user: appuser (password: ${DB_PASSWORD})"
echo "Port: ${DB_PORT}"
echo ""

echo "To connect to the database, use the following command:"
echo "$(cat db_connection.txt)"

# Keep running
wait