import sqlite3
import uuid
import random

class DatabaseSetup:
    def __init__(self, db_name="finance_platform.db"):
        self.db_name = db_name

    def initialize_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        tables = [
            """CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY, login TEXT UNIQUE, password TEXT, role TEXT)""",
            """CREATE TABLE IF NOT EXISTS assets (
                asset_id TEXT PRIMARY KEY, ticker TEXT, title TEXT, asset_type TEXT)""",
            """CREATE TABLE IF NOT EXISTS quotes (
                quote_id TEXT PRIMARY KEY, time TEXT, opening_price REAL, closing_price REAL,
                max_price REAL, min_price REAL, volume INTEGER, asset_id TEXT,
                FOREIGN KEY(asset_id) REFERENCES assets(asset_id))""",
            """CREATE TABLE IF NOT EXISTS news (
                news_id TEXT PRIMARY KEY, source TEXT, heading TEXT, text TEXT,
                publication_time TEXT, sentiment TEXT, asset_id TEXT)""",
            """CREATE TABLE IF NOT EXISTS forecasts (
                forecast_id TEXT PRIMARY KEY, creation_time TEXT, forecast_horizon TEXT,
                target_value REAL, accuracy REAL, asset_id TEXT)""",
            """CREATE TABLE IF NOT EXISTS recommendations (
                recommendation_id TEXT PRIMARY KEY, rec_type TEXT, target_price REAL,
                stop_loss REAL, status TEXT, asset_id TEXT)""",
            """CREATE TABLE IF NOT EXISTS portfolios (
                portfolio_id TEXT PRIMARY KEY, title TEXT, user_id TEXT)""",
            """CREATE TABLE IF NOT EXISTS positions (
                position_id TEXT PRIMARY KEY, quantity REAL, average_purchase_price REAL,
                asset_id TEXT, portfolio_id TEXT)""",
            """CREATE TABLE IF NOT EXISTS bots (
                bot_id TEXT PRIMARY KEY, name TEXT, strategy TEXT, assets TEXT,
                stop_loss REAL, take_profit REAL, max_pos REAL, user_id TEXT)"""
        ]

        for query in tables:
            cursor.execute(query)

        self._seed_data(cursor)
        conn.commit()
        conn.close()

    def _seed_data(self, cursor):
        cursor.execute("SELECT count(*) FROM assets")
        if cursor.fetchone()[0] > 0:
            return

        assets = [
            ("1", "AAPL", "Apple Inc.", "Stock"),
            ("2", "BTC", "Bitcoin", "Crypto"),
            ("3", "TSLA", "Tesla Inc.", "Stock"),
            ("4", "GOOGL", "Google LLC", "Stock"),
            ("5", "EURUSD", "Euro/Dollar", "Forex")
        ]
        cursor.executemany("INSERT INTO assets VALUES (?,?,?,?)", assets)

        users = [
            (str(uuid.uuid4()), "investor", "123", "Investor"),
            (str(uuid.uuid4()), "analyst", "123", "Analyst"),
            (str(uuid.uuid4()), "manager", "123", "Manager")
        ]
        cursor.executemany("INSERT OR IGNORE INTO users VALUES (?,?,?,?)", users)

        for asset in assets:
            price = 150.0
            if asset[1] == "BTC": price = 30000.0
            
            for i in range(50):
                change = random.uniform(-0.02, 0.02)
                price = price * (1 + change)
                cursor.execute("INSERT INTO quotes VALUES (?,?,?,?,?,?,?,?)", 
                               (str(uuid.uuid4()), f"2023-10-{i+1:02d}", price, price * (1+random.uniform(-0.01, 0.01)), 
                                price * 1.05, price * 0.95, random.randint(1000, 50000), asset[0]))

    def reset_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        tables = ["users", "assets", "quotes", "news", "forecasts", "recommendations", "portfolios", "positions", "bots"]
        for t in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {t}")
        conn.commit()
        conn.close()
        self.initialize_db()