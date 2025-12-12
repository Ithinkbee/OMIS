import sqlite3
import uuid
from typing import List, Any

class User:
    def __init__(self, user_id, login, password, role):
        self.user_id = user_id
        self.login = login
        self.password = password
        self.role = role
    
    def __repr__(self):
        return f"<User {self.login} ({self.role})>"

class PrivateInvestor(User):
    def __init__(self, user_id, login, password):
        super().__init__(user_id, login, password, "Investor")

class FinancialAnalyst(User):
    def __init__(self, user_id, login, password):
        super().__init__(user_id, login, password, "Analyst")
    
class FundManager(User):
    def __init__(self, user_id, login, password):
        super().__init__(user_id, login, password, "Manager")

class AnalysisContext:
    def __init__(self, user_id, assets_list, time_interval):
        self.user_id = user_id
        self.assets_list = assets_list
        self.time_interval = time_interval

class Asset:
    def __init__(self, asset_id, ticker, title, asset_type):
        self.asset_id = asset_id
        self.ticker = ticker
        self.title = title
        self.asset_type = asset_type
    
    def __repr__(self):
        return f"{self.ticker}"

class TradingBot:
    def __init__(self, bot_id, name, strategy, assets, stop_loss, take_profit, max_pos, user_id):
        self.bot_id = bot_id
        self.name = name
        self.strategy = strategy
        self.assets = assets
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.max_pos = max_pos
        self.user_id = user_id

class Repository:
    def __init__(self, connection):
        self.conn = connection

    def getObject(self, table, id_column, id_value):
        cursor = self.conn.cursor()
        query = f"SELECT * FROM {table} WHERE {id_column} = ?"
        cursor.execute(query, (id_value,))
        return cursor.fetchone()

    def saveObject(self, object) -> None:
        raise NotImplementedError("Save logic is specific to the entity")

    def deleteObject(self, table, id_column, id_value) -> None:
        cursor = self.conn.cursor()
        query = f"DELETE FROM {table} WHERE {id_column} = ?"
        cursor.execute(query, (id_value,))
        self.conn.commit()

class Quote:
    def __init__(self, qote_id, time, open_p, close_p, max_p, min_p, vol, asset_id):
        self.qote_id = qote_id
        self.time = time
        self.opening_price = open_p
        self.closing_price = close_p
        self.max_price = max_p
        self.min_price = min_p
        self.volume = vol
        self.asset_id = asset_id

class News:
    def __init__(self, news_id, source, heading, text, pub_time, sentiment, asset_id):
        self.news_id = news_id
        self.source = source
        self.heading = heading
        self.text = text
        self.publication_time = pub_time
        self.sentiment = sentiment
        self.asset_id = asset_id

class DataRepository(Repository):
    def getQuotes(self, asset_id, period) -> List[Quote]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM quotes WHERE asset_id = ? ORDER BY time", (asset_id,))
        return [Quote(*row) for row in cursor.fetchall()]

    def getNews(self, asset_id, period) -> List[News]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM news WHERE asset_id = ?", (asset_id,))
        return [News(*row) for row in cursor.fetchall()]
    
    def getAllAssets(self) -> List[Asset]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM assets")
        return [Asset(*row) for row in cursor.fetchall()]
    
    def saveObject(self, object) -> None:
        if isinstance(object, Quote):
            cursor = self.conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO quotes VALUES (?,?,?,?,?,?,?,?)",
                           (object.qote_id, object.time, object.opening_price, object.closing_price, 
                            object.max_price, object.min_price, object.volume, object.asset_id))
            self.conn.commit()

class Report:
    def __init__(self, report_id, title, period, content, metrics=None):
        self.report_id = report_id
        self.title = title
        self.period = period
        self.content = content
        self.metrics = metrics or {}

class ReportRepository(Repository):
    def getReport(self, report_id) -> Report:
        return Report(report_id, "Generated Report", "N/A", "Content loaded from archive")

    def createReport(self, params) -> Report:
        return Report(str(uuid.uuid4()), params['title'], params['period'], params['content'])
    
    def saveObject(self, object) -> None:
        print(f"[DB LOG] Report {object.report_id} saved (simulated).")

class Forecast:
    def __init__(self, f_id, time, horizon, target, accuracy, asset_id):
        self.forecast_id = f_id
        self.creation_time = time
        self.forecast_horizon = horizon
        self.target_value = target
        self.accuracy = accuracy
        self.asset_id = asset_id

class ForecastRepository(Repository):
    def getForecasts(self, context) -> List[Forecast]:
        cursor = self.conn.cursor()
        if not context.assets_list: return []
        asset_id = context.assets_list[0]
        cursor.execute("SELECT * FROM forecasts WHERE asset_id = ?", (asset_id,))
        return [Forecast(*row) for row in cursor.fetchall()]

    def saveForecast(self, forecast) -> None:
        self.saveObject(forecast)

    def saveObject(self, obj) -> None:
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO forecasts VALUES (?,?,?,?,?,?)", 
                       (obj.forecast_id, obj.creation_time, obj.forecast_horizon, 
                        obj.target_value, obj.accuracy, obj.asset_id))
        self.conn.commit()

class Recommendation:
    recommendation_type = {"buy", "sell", "hold"}
    def __init__(self, r_id, r_type, target, stop, status, asset_id):
        self.recommendation_id = r_id
        self.rec_value = r_type if r_type in self.recommendation_type else "hold"
        self.target_price = target
        self.stop_Loss = stop
        self.status = status
        self.asset_id = asset_id

class RecommendationRepository(Repository):
    def getRecommendations(self, context) -> List[Recommendation]:
        cursor = self.conn.cursor()
        if not context.assets_list: return []
        asset_id = context.assets_list[0]
        cursor.execute("SELECT * FROM recommendations WHERE asset_id = ?", (asset_id,))
        return [Recommendation(*row) for row in cursor.fetchall()]

    def saveRecommendation(self, recommendation) -> None:
        self.saveObject(recommendation)

    def saveObject(self, obj) -> None:
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO recommendations VALUES (?,?,?,?,?,?)",
                       (obj.recommendation_id, obj.rec_value, obj.target_price,
                        obj.stop_Loss, obj.status, obj.asset_id))
        self.conn.commit()

class Position:
    def __init__(self, p_id, qty, avg_price, asset_id, portfolio_id=None):
        self.position_id = p_id
        self.quantity = qty
        self.average_purchase_price = avg_price
        self.asset_id = asset_id
        self.portfolio_id = portfolio_id

class Portfolio:
    def __init__(self, p_id, title, user_id):
        self.portfolio_id = p_id
        self.title = title
        self.user_id = user_id
        self.positions = [] 

class PortfolioRepository(Repository):
    def getPortfolio(self, user_id) -> Portfolio:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM portfolios WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row: return None
        
        portfolio = Portfolio(*row)
        cursor.execute("SELECT * FROM positions WHERE portfolio_id = ?", (portfolio.portfolio_id,))
        pos_rows = cursor.fetchall()
        portfolio.positions = [Position(*r) for r in pos_rows]
        return portfolio

    def savePortfolio(self, portfolio) -> None:
        self.saveObject(portfolio)

    def saveObject(self, obj) -> None:
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO portfolios VALUES (?,?,?)", 
                       (obj.portfolio_id, obj.title, obj.user_id))
        
        cursor.execute("DELETE FROM positions WHERE portfolio_id = ?", (obj.portfolio_id,))
        for pos in obj.positions:
            cursor.execute("INSERT INTO positions VALUES (?,?,?,?,?)",
                           (pos.position_id, pos.quantity, pos.average_purchase_price, pos.asset_id, obj.portfolio_id))
        self.conn.commit()

class UserRepository(Repository):
    def get_user(self, login, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_id, login, password, role FROM users WHERE login=? AND password=?", (login, password))
        row = cursor.fetchone()
        if row: return User(*row)
        return None
    
    def register_user(self, user):
        self.saveObject(user)

    def saveObject(self, user) -> None:
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users VALUES (?,?,?,?)", (user.user_id, user.login, user.password, user.role))
        self.conn.commit()

class BotRepository(Repository):
    def saveBot(self, bot: TradingBot):
        self.saveObject(bot)

    def saveObject(self, bot) -> None:
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO bots VALUES (?,?,?,?,?,?,?,?)", 
                       (bot.bot_id, bot.name, bot.strategy, bot.assets, bot.stop_loss, bot.take_profit, bot.max_pos, bot.user_id))
        self.conn.commit()
    
    def getBots(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM bots WHERE user_id=?", (user_id,))
        return [TradingBot(*r) for r in cursor.fetchall()]