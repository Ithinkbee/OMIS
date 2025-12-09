import string
from model import Forecast, Portfolio, Recommendation, Report
from typing import List

#зависит от ForecastRepository
class ForecastController:
    def createForecast(self, context) -> Forecast:
        pass

    def getForecasts(self) -> List[Forecast]:
        pass

#зависит от ReportRepository
class ReportController:
    def generateReport(self, period: str) -> Report:
        pass

    def getReports(self) -> List[Report]:
        pass

class IAnalysisStrategy:
    def analyse(self, data: List) -> List:
        pass

#технический анализ
class TechnicalAnalysisStrategy(IAnalysisStrategy):
    pass

#анализ настроений
class SentimentAnalysisStrategy(IAnalysisStrategy):
    pass

#зависит от DataRepository
class AnalysisController:
    #используется стратегия анализа
    def analyseData(self) -> None:
        pass

    def getAnalytics(self) -> List:
        pass

#зависит от DataRepository
class DashboardController:
    def startMonitoring(self) -> None:
        pass

    def getDashboardData(self) -> List:
        pass

#зависит от RecommendationRepository
class RecommendationController:
    def generateRecommendations(self, context) -> List[Recommendation]:
        pass

    def getRecommendations(self) -> List[Recommendation]:
        pass

class ICommand:
    def execute(self) -> None:
        pass

    def abort(self) -> None:
        pass

class BuyAssetCommand(ICommand):
    pass

class SellAssetCommand(ICommand):
    pass

#зависит от PortfolioRepository
class PortfolioManagementController:
    def createPortfolio(self, title) -> Portfolio:
        pass

    def buyAsset(self, asset, quantity) -> None:
        pass

    def sellAsset(self, asset, quantity) -> None:
        pass








