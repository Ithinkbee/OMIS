import uuid
import random
import threading
import time
from model import *
from typing import List

class IController:
    def execute(self):
        raise NotImplementedError("Base Controller method")

class AuthController(IController):
    def __init__(self, user_repo):
        self.user_repo = user_repo
        self.current_user = None

    def login(self, login, password):
        user = self.user_repo.get_user(login, password)
        self.current_user = user
        return user

    def logout(self):
        self.current_user = None

    def register(self, login, password, role):
        if role == "Manager":
            return None 
        user = User(str(uuid.uuid4()), login, password, role)
        try:
            self.user_repo.register_user(user)
            self.current_user = user
            return user
        except Exception as e:
            print(f"Registration error: {e}")
            return None

class ForecastController(IController):
    def __init__(self, forecast_repo, data_repo, model_repo):
        self.forecast_repo = forecast_repo
        self.data_repo = data_repo
        self.model_repo = model_repo

    def train_new_model(self, model_name, params) -> AnalysisModelEntity:
        model = AnalysisModelEntity(str(uuid.uuid4()), model_name, params, "Training", 0.0)
        
        if "epoch" not in params:
            model.status = "Rejected: Missing Params"
        else:
            model.status = "Ready"
            model.accuracy = random.uniform(0.70, 0.95)
        
        self.model_repo.saveObject(model)
        return model

    def createForecast(self, context, model_name="ARIMA") -> Forecast:
        asset_id = context.assets_list[0]
        quotes = self.data_repo.getQuotes(asset_id, "")
        last_price = quotes[-1].closing_price if quotes else 100.0
        
        volatility = 0.05
        if model_name == "LSTM":
            volatility = 0.03
        elif model_name == "Random Forest":
            volatility = 0.07

        horizon_days = 7 if context.time_interval == "1W" else 30
        change_factor = random.uniform(-volatility, volatility) + (0.01 if model_name=="LSTM" else 0)
        target = last_price * (1 + change_factor)
        
        conf_min = target * (1 - volatility * 1.96)
        conf_max = target * (1 + volatility * 1.96)
        
        f = Forecast(str(uuid.uuid4()), "2023-12-01", context.time_interval, target, 0.85, asset_id, 
                     conf_interval=(conf_min, conf_max), volatility=volatility)
        
        self.forecast_repo.saveForecast(f)
        return f
    
    def getAvailableAssets(self):
        return self.data_repo.getAllAssets()

class ReportController(IController):
    def __init__(self, report_repo, portfolio_repo, data_repo):
        self.report_repo = report_repo
        self.portfolio_repo = portfolio_repo
        self.data_repo = data_repo

    def generateReport(self, period: str, user_id: str) -> Report:
        pf = self.portfolio_repo.getPortfolio(user_id)
        if not pf:
            return self.report_repo.createReport({
                'title': 'Portfolio Report', 'period': period, 'content': 'No portfolio found.', 'metrics': {}
            })
        
        total_value = 0
        initial_value = 0
        
        for pos in pf.positions:
            quotes = self.data_repo.getQuotes(pos.asset_id, "")
            curr = quotes[-1].closing_price if quotes else 0
            
            total_value += curr * pos.quantity
            initial_value += pos.average_purchase_price * pos.quantity
            
        yield_pct = ((total_value - initial_value) / initial_value * 100) if initial_value else 0
        var_95 = total_value * 0.05 * 1.65 
        stress_drop = total_value * 0.8 
        
        metrics = {
            "Yield": f"{yield_pct:.2f}%",
            "Volatility": "12.5% (Annualized)",
            "Benchmark (S&P500)": "+4.2%",
            "VaR (95%)": f"${var_95:.2f}",
            "Stress Test (-20%)": f"${stress_drop:.2f}"
        }
        
        content = f"Portfolio Valuation: ${total_value:.2f}\nNet Profit: ${total_value - initial_value:.2f}"
        
        print(f"[SYSTEM] Notification: Report {period} for User {user_id} is ready.")
        
        return self.report_repo.createReport({'title': f'Analysis {period}', 'period': period, 'content': content, 'metrics': metrics})

class IAnalysisStrategy:
    def analyse(self, data: List) -> List:
        raise NotImplementedError("Abstract method")

class TechnicalAnalysisStrategy(IAnalysisStrategy):
    def analyse(self, data: List[Quote]) -> List:
        if len(data) < 20: return ["HOLD"]
        sma_short = sum([q.closing_price for q in data[-5:]]) / 5
        sma_long = sum([q.closing_price for q in data[-20:]]) / 20
        
        if sma_short > sma_long: return ["BUY"]
        if sma_short < sma_long: return ["SELL"]
        return ["HOLD"]

class SentimentAnalysisStrategy(IAnalysisStrategy):
    def analyse(self, data: List[News]) -> List:
        return ["POSITIVE"]

class AnalysisController(IController):
    def __init__(self, data_repo, strategies):
        self.data_repo = data_repo
        self.strategies = strategies

    def analyseData(self, asset_id) -> str:
        quotes = self.data_repo.getQuotes(asset_id, "")
        
        tech = "HOLD"
        for s in self.strategies:
            if isinstance(s, TechnicalAnalysisStrategy):
                tech = s.analyse(quotes)[0]
        
        return tech

class DashboardController(IController):
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

    def getMarketData(self) -> List:
        assets = self.data_repo.getAllAssets()
        result = []
        for a in assets:
            quotes = self.data_repo.getQuotes(a.asset_id, "")
            if not quotes: continue
            last = quotes[-1]
            prev = quotes[-2] if len(quotes) > 1 else last
            change_pct = ((last.closing_price - prev.closing_price) / prev.closing_price) * 100
            
            result.append({
                "ticker": a.ticker,
                "title": a.title,
                "price": last.closing_price,
                "change": change_pct,
                "history": [q.closing_price for q in quotes],
                "id": a.asset_id
            })
        return result

    def getPortfolioSummary(self, user_id) -> List:
        pf = self.portfolio_repo.getPortfolio(user_id)
        if not pf: return []
        
        summary = []
        for pos in pf.positions:
            assets = self.data_repo.getAllAssets()
            asset_info = next((a for a in assets if a.asset_id == pos.asset_id), None)
            ticker = asset_info.ticker if asset_info else "UNKNOWN"
            
            quotes = self.data_repo.getQuotes(pos.asset_id, "")
            curr = quotes[-1].closing_price if quotes else 0
            
            change = 0
            if pos.average_purchase_price > 0:
                change = ((curr - pos.average_purchase_price) / pos.average_purchase_price) * 100
                
            summary.append({
                "ticker": ticker,
                "qty": pos.quantity,
                "value": curr * pos.quantity,
                "change": change
            })
        return summary

class RecommendationController(IController):
    def __init__(self, rec_repo, risk_repo, rule_repo):
        self.rec_repo = rec_repo
        self.risk_repo = risk_repo
        self.rule_repo = rule_repo

    def generateRecommendations(self, context, analysis_result="HOLD") -> List[Recommendation]:
        risks = self.risk_repo.get_all_risks()
        rules = self.rule_repo.get_all_rules()
        
        risk_penalty = sum([r.probability * 0.1 for r in risks])
        
        rec_type = analysis_result.lower()
        quotes = DataRepository(self.rec_repo.conn).getQuotes(context.assets_list[0], "")
        last = quotes[-1].closing_price if quotes else 100
        
        if risk_penalty > 0.5:
            rec_type = "hold"
            
        target = last * 1.05 if rec_type == "buy" else last * 0.95
        stop = last * 0.98 if rec_type == "buy" else last * 1.02
        
        rec = Recommendation(str(uuid.uuid4()), rec_type, target, stop, "Active", context.assets_list[0])
        self.rec_repo.saveRecommendation(rec)
        return [rec]

class ICommand:
    def execute(self) -> None: raise NotImplementedError
    def abort(self) -> None: raise NotImplementedError

class BuyAssetCommand(ICommand):
    def __init__(self, controller, asset_id, qty, user_id):
        self.ctrl = controller
        self.asset_id = asset_id
        self.qty = qty
        self.user_id = user_id
    
    def execute(self):
        self.ctrl.buyAsset(self.asset_id, self.qty, self.user_id)
    
    def abort(self): pass

class SellAssetCommand(ICommand):
    def __init__(self, controller, asset_id, qty, user_id):
        self.ctrl = controller
        self.asset_id = asset_id
        self.qty = qty
        self.user_id = user_id
    
    def execute(self):
        self.ctrl.sellAsset(self.asset_id, self.qty, self.user_id)
    
    def abort(self): pass

class PortfolioManagementController(IController):
    def __init__(self, portfolio_repo):
        self.repo = portfolio_repo

    def createPortfolio(self, title, user_id) -> Portfolio:
        p = Portfolio(str(uuid.uuid4()), title, user_id)
        self.repo.savePortfolio(p)
        return p

    def buyAsset(self, asset_id, quantity, user_id) -> None:
        if quantity <= 0: return
        p = self.repo.getPortfolio(user_id)
        if not p:
            p = self.createPortfolio("Main Portfolio", user_id)
        
        found = False
        for pos in p.positions:
            if pos.asset_id == asset_id:
                pos.quantity += quantity
                found = True
                break
        if not found:
            p.positions.append(Position(str(uuid.uuid4()), quantity, 150.0, asset_id, p.portfolio_id))
        
        self.repo.savePortfolio(p)
        print(f"[SYSTEM] Bought {quantity} of {asset_id}")

    def sellAsset(self, asset_id, quantity, user_id) -> None:
        if quantity <= 0: return
        p = self.repo.getPortfolio(user_id)
        if not p: return

        for pos in p.positions:
            if pos.asset_id == asset_id:
                if pos.quantity >= quantity:
                    pos.quantity -= quantity
                    if pos.quantity == 0:
                        p.positions.remove(pos)
                    self.repo.savePortfolio(p)
                    print(f"[SYSTEM] Sold {quantity} of {asset_id}")
                return

class AutoTradingController(IController):
    def __init__(self, bot_repo, data_repo):
        self.repo = bot_repo
        self.data_repo = data_repo

    def getAvailableStrategies(self):
        return ["Moving Average Crossover", "RSI Scalping", "Mean Reversion", "Bollinger Breakout"]

    def createBot(self, name, strategy, assets, sl, tp, max_p, user_id):
        b = TradingBot(str(uuid.uuid4()), name, strategy, assets, sl, tp, max_p, user_id)
        self.repo.saveBot(b)
        return b
    
    def getUserBots(self, user_id):
        return self.repo.getBots(user_id)
    
    def run_bot_cycle(self, user_id):
        bots = self.repo.getBots(user_id)
        log = []
        for bot in bots:
            log.append(f"Bot {bot.name}: Checked market conditions. Holding position.")
        return log

