# create-prisma-app

`create-prisma-app` is a Python-powered CLI that bootstraps a Node.js + Express + Prisma project with PostgreSQL.

## 🚀 Features
- Sets up an Express server
- Configures Prisma ORM
- Auto-generates database migrations
- Adds Jest for testing
- Includes a sample health check & database connection test

## 📦 Installation

Using [pipx](https://pypa.github.io/pipx/):

## Usage
usage: create-prisma-app [-h] --db-name DB_NAME --db-user DB_USER --db-pass DB_PASS project_name

Express + Prisma Bootstrap CLI

positional arguments:
  project_name       Project name

options:
  -h, --help         show this help message and exit
  --db-name DB_NAME  Database Name
  --db-user DB_USER  Database User
  --db-pass DB_PASS  Database Password

```bash
pipx install create-prisma-app
