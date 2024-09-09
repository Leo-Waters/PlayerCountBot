# Step 1: Use an official Python runtime as a base image
FROM python:3.10-slim

# Step 2: Set the working directory in the container
WORKDIR /usr/src/app

# Step 3: Install system dependencies required for MariaDB and Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev-compat \
    libmariadb-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Step 4: Copy the current directory contents into the container at /usr/src/app
COPY . .

# Step 5: Install any Python dependencies (discord.py, mariadb, pymysql)
RUN pip install --no-cache-dir discord.py pymysql mariadb

# Step 6: Expose any necessary ports (none needed for this bot)
# EXPOSE 8080 (optional, not needed for Discord bot)

# Step 7: Run the bot when the container launches
CMD [ "python", "./bot.py" ]

