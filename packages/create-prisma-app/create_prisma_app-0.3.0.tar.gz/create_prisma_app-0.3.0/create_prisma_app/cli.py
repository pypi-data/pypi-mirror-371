#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import json
from pathlib import Path
import urllib.parse

# ------------------------
# Helpers
# ------------------------

def print_output(process):
    for line in process.stdout:
        print(line, end="", flush=True)
    process.wait()


def check_installation(cmd, install_cmd=None):
    try:
        res = subprocess.run([cmd, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"[✓] {cmd} is installed ({res.stdout.strip()})")
    except Exception:
        prompt = input(f"[x] {cmd} not found. Install it? (y/n): ").lower()
        if prompt in {"y", "yes"}:
            if not install_cmd:
                print(f"No install command for {cmd}. Please install manually.")
                sys.exit(1)
            print(f"[...] Installing {cmd}...\n")
            process = subprocess.Popen(install_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            print_output(process)
            if process.returncode == 0:
                print(f"[✓] {cmd} installed successfully!")
            else:
                print(f"[x] Failed to install {cmd}. Exiting.")
                sys.exit(1)
        else:
            print(f"Skipping {cmd}. This may cause errors.")


# ------------------------
# Postgres
# ------------------------

def setup_postgres(db_name, db_user, db_pass):
    print(f"\n[Postgres] Ensuring DB '{db_name}' and user '{db_user}' exist...")

    sql = f"""
DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{db_user}') THEN
      CREATE ROLE {db_user} LOGIN PASSWORD '{db_pass}' CREATEDB;
   ELSE
      ALTER ROLE {db_user} WITH LOGIN PASSWORD '{db_pass}' CREATEDB;
   END IF;
END
$do$;

DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '{db_name}') THEN
      CREATE DATABASE {db_name} OWNER {db_user};
   END IF;
END
$do$;
"""

    try:
        process = subprocess.Popen(
            ["sudo", "-u", "postgres", "psql", "-v", "ON_ERROR_STOP=1"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        process.communicate(sql)
        if process.returncode == 0:
            print(f"[✓] Database '{db_name}' and user '{db_user}' ready.\n")
        else:
            print("[x] Failed to create database/user. Check Postgres logs.")
            sys.exit(1)
    except Exception as e:
        print(f"[x] Error: {e}")
        sys.exit(1)


# ------------------------
# Project Scaffold
# ------------------------

def create_project_structure(project_name, db_url):
    print(f"[...] Creating project '{project_name}' structure...")
    base = Path(project_name)
    os.makedirs(base / "src" / "routes", exist_ok=True)
    os.makedirs(base / "tests", exist_ok=True)
    os.makedirs(base / "prisma", exist_ok=True)

    (base / ".env").write_text(f'DATABASE_URL="{db_url}"\n')

    # app.js
    (base / "src" / "app.js").write_text(
        """const express = require("express");
const app = express();
app.get("/health", (req, res) => res.json({status: "OK"}));
module.exports = app;
"""
    )

    # server.js
    (base / "server.js").write_text(
        """const app = require("./src/app");
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
"""
    )

    # Prisma schema
    schema_file = base / "prisma" / "schema.prisma"
    if not schema_file.exists():
        schema_file.write_text(
            """generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id    Int     @id @default(autoincrement())
  email String  @unique
  name  String?
}
"""
        )

    # Test file
    (base / "tests" / "app.test.js").write_text(
        """const request = require("supertest");
const app = require("../src/app");
const { PrismaClient } = require("@prisma/client");

const prisma = new PrismaClient();

describe("Health check", () => {
  it("GET /health", async () => {
    const res = await request(app).get("/health");
    expect(res.statusCode).toBe(200);
  });

  it("Database connection", async () => {
    const result = await prisma.$queryRaw`SELECT 1 as number`;
    expect(result[0].number).toBe(1);
  });
});
"""
    )

    print(f"[✓] Project structure created at {base}\n")


# ------------------------
# Node Setup
# ------------------------

def setup_node_dependencies(project_name):
    os.chdir(project_name)
    print("📦 Installing dependencies...")
    subprocess.run(["npm", "install", "express", "@prisma/client"], check=True)
    subprocess.run(["npm", "install", "--save-dev", "jest", "supertest", "dotenv"], check=True)

    if not Path("prisma").exists():
        subprocess.run(["npx", "prisma", "init"], check=True)
    else:
        print("⚠️  Skipping `prisma init` because `prisma/` exists.")

    # Add Jest config
    with open("package.json", "r") as f:
        pkg = json.load(f)
    pkg.setdefault("scripts", {})
    pkg["scripts"]["test"] = "jest"
    pkg["jest"] = {"setupFiles": ["<rootDir>/jest.setup.js"]}
    with open("package.json", "w") as f:
        json.dump(pkg, f, indent=2)

    # jest.setup.js
    (Path("jest.setup.js")).write_text('require("dotenv").config();\n')

    # Run Prisma migrations
    print("\n🚀 Running Prisma migrations...")
    subprocess.run(["npx", "prisma", "migrate", "dev", "--name", "init"], check=True)
    print("✅ Dependencies installed and Prisma migrations applied.")


# ------------------------
# CLI Entry
# ------------------------

def main():
    parser = argparse.ArgumentParser(description="Express + Prisma Bootstrap CLI")
    parser.add_argument("project_name", help="Project name")
    parser.add_argument("--db-name", required=True, help="Database Name")
    parser.add_argument("--db-user", required=True, help="Database User")
    parser.add_argument("--db-pass", required=True, help="Database Password")
    args = parser.parse_args()

    # Dependency checks
    check_installation("node", ["sudo", "apt", "install", "-y", "nodejs", "npm"])
    check_installation("npm", ["sudo", "apt", "install", "-y", "npm"])
    check_installation("psql", ["sudo", "apt", "install", "-y", "postgresql-client"])
    check_installation("prisma", ["sudo", "npm", "install", "-g", "prisma"])

    # Postgres
    setup_postgres(args.db_name, args.db_user, args.db_pass)

    # Encode password for URL
    password_encoded = urllib.parse.quote(args.db_pass)
    db_url = f"postgresql://{args.db_user}:{password_encoded}@localhost:5432/{args.db_name}?schema=public"

    # Scaffold
    create_project_structure(args.project_name, db_url)

    # Node deps & migrations
    setup_node_dependencies(args.project_name)

    print(f"\n[✓] Project {args.project_name} ready! Run:")
    print(f"   cd {args.project_name}")
    print(f"   npm test   # run tests")
    print(f"   node server.js   # start server")


if __name__ == "__main__":
    main()
