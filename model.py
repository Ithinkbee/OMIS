import string
from typing import List 

#абстрактный класс
class User:
    user_id = None #уникально среди других таких же объектов #String
    login = None #String

class PrivateInvestor(User):
    def __init__(self):
        pass

class FinancialAnalyst(User):
    def __init__(self):
        pass
    
#может быть только один
class FundManager(User):
    def __init__(self):
        pass

class AnalysisContext:
    user_id = None 
    assets_list = None #List[String]
    time_interval = None

    def __init__(self):
        pass

class Asset:
    asset_id = None #уникально среди других таких же объектов
    ticker = None
    title = None
    asset_type = None

    def __init__(self):
        pass

#абстрактный класс
class Repository:
    def getObject(self, id):
        pass

    def saveObject(self, object) -> None:
        pass

    def deleteObject(self, id) -> None:
        pass

class Quote:
    qote_id = None #уникально среди других таких же объектов
    time = None
    opening_price = None
    closing_price = None
    max_price = None
    min_price = None
    volume = None

    def __init__(self):
        pass

class News:
    news_id = None #уникально среди других таких же объектов
    source = None
    heading = None
    text = None
    publication_time = None
    sentiment = None

    def __init__(self):
        pass

#может быть только один
class DataRepository(Repository):
    def getQuotes(self, asset_id, period) -> List[Quote]:
        pass

    def getNews(self, asset_id, period) -> List[News]:
        pass

class Report:
    report_id = None #уникально среди других таких же объектов
    title = None
    period = None
    content = None

    def __init__(self):
        pass

#может быть только один
class ReportRepository(Repository):
    def getReport(self, report_id) -> Report:
        pass

    def createReport(self, params) -> Report:
        pass

class Forecast:
    forecast_id = None #уникально среди других таких же объектов
    creation_time = None
    forecast_horizon = None
    target_value = None
    accuracy = None

    def __init__(self):
        pass

#может быть только один
class ForecastRepository(Repository):
    def getForecasts(self, context) -> List[Forecast]:
        pass

    def saveForecast(self, forecast) -> None:
        pass

class Recommendation:
    recommendation_id = None #уникально среди других таких же объектов
    recommendation_type = {buy, sell, hold} #одно из этих значений
    target_price = None
    stop_Loss = None
    status = None

    def __init__(self):
        pass

#может быть только один
class RecommendationRepository(Repository):
    def getRecommendations(self, context) -> List[Recommendation]:
        pass

    def saveRecommendation(self, recommendation) -> None:
        pass

#существует только внутри Portfolio
class Position:
    position_id = None #уникально среди других таких же объектов
    quantity = None
    average_purchase_price = None

    def __init__(self):
        pass

class Portfolio:
    portfolio_id = None #уникально среди других таких же объектов
    title = None
    positions = None #List[Position]

    def __init__(self):
        pass

#может быть только один
class PortfolioRepository(Repository):
    def getPortfolio(self, user_id) -> Portfolio:
        pass

    def savePortfolio(self, portfolio) -> None:
        pass


