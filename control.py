import string
import uuid
import random
import threading
import time
from model import *
from typing import List

class AuthController:
    def __init__(self, user_repo):
        self.user_repo = user_repo
        self.current_user = None

    def login(self, login, password):
        user = self.user_repo.get_user(login, password)
        self.current_user = user
        return user

    def register(self, login, password, role):
        user = User(str(uuid.uuid4()), login, password, role)
        try:
            self.user_repo.register_user(user)
            self.current_user = user
            return user
        except Exception as e:
            print(f"Registration error: {e}")
            return None

class ForecastController:
    def __init__(self, forecast_repo, data_repo):
        self.forecast_repo = forecast_repo
        self.data_repo = data_repo

    def createForecast(self, context) -> Forecast:
        asset_id = context.assets_list[0]
        quotes = self.data_repo.getQuotes(asset_id, "")
        last_price = quotes[-1].closing_price if quotes else 100.0
        
        multiplier = 1.0
        if context.time_interval == "1W": multiplier = random.uniform(0.98, 1.05)
        elif context.time_interval == "1M": multiplier = random.uniform(0.90, 1.15)
        
        target = last_price * multiplier
        acc = random.uniform(0.7, 0.95)
        
        f = Forecast(str(uuid.uuid4()), "2023-12-01", context.time_interval, target, acc, asset_id)
        self.forecast_repo.saveForecast(f)
        return f

    def getForecasts(self, context) -> List[Forecast]:
        return self.forecast_repo.getForecasts(context)
    
    def getAvailableAssets(self):
        return self.data_repo.getAllAssets()

class ReportController:
    def __init__(self, report_repo, portfolio_repo, data_repo):
        self.report_repo = report_repo
        self.portfolio_repo = portfolio_repo
        self.data_repo = data_repo

    def generateReport(self, period: str, user_id: str) -> Report:
        pf = self.portfolio_repo.getPortfolio(user_id)
        if not pf:
            return self.report_repo.createReport({'title': 'Empty Report', 'period': period, 'content': 'No portfolio found.'})
        
        total_value = 0
        details = []
        for pos in pf.positions:
            quotes = self.data_repo.getQuotes(pos.asset_id, "")
            curr = quotes[-1].closing_price if quotes else 0
            val = curr * pos.quantity
            total_value += val
            details.append(f"{pos.asset_id}: {pos.quantity} @ {curr:.2f} = {val:.2f}")
            
        content = f"Total Value: ${total_value:.2f}\n\nAssets:\n" + "\n".join(details)
        metrics = {
            "Total Assets": str(len(pf.positions)),
            "Value": f"${total_value:.2f}",
            "Risk Level": "Medium" if total_value > 10000 else "Low"
        }
        return Report(str(uuid.uuid4()), f"Report {period}", period, content, metrics)

    def getReports(self) -> List[Report]:
        return []

class IAnalysisStrategy:
    def analyse(self, data: List) -> List:
        raise NotImplementedError("Abstract method")

class TechnicalAnalysisStrategy(IAnalysisStrategy):
    def analyse(self, data: List[Quote]) -> List:
        if len(data) < 2: return ["HOLD"]
        prices = [q.closing_price for q in data]
        avg = sum(prices) / len(prices)
        last = prices[-1]
        
        if last > avg * 1.01: return ["BUY"]
        if last < avg * 0.99: return ["SELL"]
        return ["HOLD"]

class SentimentAnalysisStrategy(IAnalysisStrategy):
    def analyse(self, data: List[News]) -> List:
        if not data: return ["NEUTRAL"]
        score = 0
        for news in data:
            if news.sentiment == "POSITIVE": score += 1
            elif news.sentiment == "NEGATIVE": score -= 1
        
        if score > 0: return ["POSITIVE"]
        if score < 0: return ["NEGATIVE"]
        return ["NEUTRAL"]

class AnalysisController:
    def __init__(self, data_repo, strategies):
        self.data_repo = data_repo
        self.strategies = strategies
        self.history = []

    def analyseData(self, asset_id) -> str:
        quotes = self.data_repo.getQuotes(asset_id, "")
        news = self.data_repo.getNews(asset_id, "")
        
        tech_res = "HOLD"
        sent_res = "NEUTRAL"
        
        for s in self.strategies:
            if isinstance(s, TechnicalAnalysisStrategy):
                tech_res = s.analyse(quotes)[0]
            elif isinstance(s, SentimentAnalysisStrategy):
                sent_res = s.analyse(news)[0]
        
        decision = "HOLD"
        if tech_res == "BUY" and sent_res != "NEGATIVE": decision = "BUY"
        elif tech_res == "SELL" and sent_res != "POSITIVE": decision = "SELL"
        
        self.history.append(f"Asset: {asset_id} | Tech: {tech_res} | Sent: {sent_res} -> {decision}")
        return decision

    def getAnalytics(self) -> List:
        return self.history

class DashboardController:
    def __init__(self, data_repo, portfolio_repo):
        self.data_repo = data_repo
        self.portfolio_repo = portfolio_repo
        self.monitoring = False

    def startMonitoring(self) -> None:
        if not self.monitoring:
            self.monitoring = True
            t = threading.Thread(target=self._monitor)
            t.daemon = True
            t.start()

    def _monitor(self):
        while self.monitoring:
            time.sleep(30)

    def getDashboardData(self) -> List:
        assets = self.data_repo.getAllAssets()
        result = []
        for a in assets:
            quotes = self.data_repo.getQuotes(a.asset_id, "")
            if not quotes: continue
            last = quotes[-1]
            prev = quotes[-2] if len(quotes) > 1 else last
            change = ((last.closing_price - prev.closing_price) / prev.closing_price) * 100
            result.append({
                "ticker": a.ticker,
                "price": last.closing_price,
                "change": change,
                "history": [q.closing_price for q in quotes[-20:]]
            })
        return result

class RecommendationController:
    def __init__(self, rec_repo):
        self.rec_repo = rec_repo

    def generateRecommendations(self, context) -> List[Recommendation]:
        rec = Recommendation(str(uuid.uuid4()), "buy", 200.0, 140.0, "New", context.assets_list[0])
        self.rec_repo.saveRecommendation(rec)
        return [rec]

    def getRecommendations(self, context) -> List[Recommendation]:
        return self.rec_repo.getRecommendations(context)

class ICommand:
    def execute(self) -> None: raise NotImplementedError
    def abort(self) -> None: raise NotImplementedError

class BuyAssetCommand(ICommand):
    def __init__(self, controller, asset, qty, user_id):
        self.ctrl = controller
        self.asset = asset
        self.qty = qty
        self.user_id = user_id
    
    def execute(self):
        self.ctrl.buyAsset(self.asset, self.qty, self.user_id)
    
    def abort(self):
        print("Buy aborted")

class SellAssetCommand(ICommand):
    def __init__(self, controller, asset, qty, user_id):
        self.ctrl = controller
        self.asset = asset
        self.qty = qty
        self.user_id = user_id
    
    def execute(self):
        self.ctrl.sellAsset(self.asset, self.qty, self.user_id)
    
    def abort(self):
        print("Sell aborted")

class PortfolioManagementController:
    def __init__(self, portfolio_repo):
        self.repo = portfolio_repo

    def createPortfolio(self, title, user_id) -> Portfolio:
        p = Portfolio(str(uuid.uuid4()), title, user_id)
        self.repo.savePortfolio(p)
        return p

    def buyAsset(self, asset, quantity, user_id) -> None:
        if quantity <= 0: return
        p = self.repo.getPortfolio(user_id)
        if not p:
            p = self.createPortfolio("Main Portfolio", user_id)
        
        found = False
        for pos in p.positions:
            if pos.asset_id == asset:
                pos.quantity += quantity
                found = True
                break
        if not found:
            p.positions.append(Position(str(uuid.uuid4()), quantity, 100.0, asset, p.portfolio_id))
        
        self.repo.savePortfolio(p)

    def sellAsset(self, asset, quantity, user_id) -> None:
        if quantity <= 0: return
        p = self.repo.getPortfolio(user_id)
        if not p: return

        for pos in p.positions:
            if pos.asset_id == asset:
                if pos.quantity >= quantity:
                    pos.quantity -= quantity
                    if pos.quantity == 0:
                        p.positions.remove(pos)
                    self.repo.savePortfolio(p)
                else:
                    print("Not enough quantity")
                return
        print("Asset not found in portfolio")

    def getPortfolio(self, user_id):
        return self.repo.getPortfolio(user_id)

class AutoTradingController:
    def __init__(self, bot_repo):
        self.repo = bot_repo

    def createBot(self, name, strategy, assets, sl, tp, max_p, user_id):
        b = TradingBot(str(uuid.uuid4()), name, strategy, assets, sl, tp, max_p, user_id)
        self.repo.saveBot(b)
        return b
    
    def getUserBots(self, user_id):
        return self.repo.getBots(user_id)
    
    def run_bot_cycle(self, user_id):
        bots = self.getUserBots(user_id)
        results = []
        for b in bots:
            action = random.choice(["BUY", "SELL", "HOLD"])
            results.append(f"Bot {b.name}: {action} on {b.assets}")
        return results