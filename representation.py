import string
from model import Forecast, News, Portfolio, Quote, Recommendation, Report
from typing import List 

#абстрактный класс
class BaseRepresentation:
    representation_id = None

    def _display(self, data) -> None:
        pass

    def _update(self, data) -> None:
        pass

#interface класс, реализующий BaseRepresentation
class IRepresentation(BaseRepresentation):
    def displayData(self, data) -> None:
        pass

    def updateData(self, data) -> None:
        pass

#агрегирует ReportController
class IReportRepresentation(IRepresentation):
    def showReport(self, report: Report) -> None:
        pass

    def exportReport(self, report: Report, format: str) -> None:
        pass

#агрегирует ForecastController
class IForecastRepresentation(IRepresentation):
    def showForecasts(self, forecasts: List[Forecast]) -> None:
        pass

    def displayTrends(self, data: List) -> None:
        pass

#агрегирует RecommendationController
class IRecommendationRepresentation(IRepresentation):
    def displayRecommendations(self, recommendations: List[Recommendation]) -> None:
        pass

    def highlightCriticals(self, recommendations: List[Recommendation]) -> None:
        pass

#агрегирует DashboardController
class IDashboardRepresentation(IRepresentation):
    def showCurrentQuotes(self, quotes: List[Quote]) -> None:
        pass

    def showNews(self, news: List[News]) -> None:
        pass

#агрегирует PortfolioManagementController
class IPortfolioRepresentation(IRepresentation):
    def showPortfolioContents(self, portfolio: Portfolio) -> None:
        pass

    def showOperationsHistory(self, operations: List) -> None:
        pass






