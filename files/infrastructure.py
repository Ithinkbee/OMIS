from pyclbr import Class
from typing import List, Any, Type
from control import *
from representation import *
from model import *

class DependencyContainer:
    def __init__(self):
        self._registry = {}

    def registerInterface(self, class_, instance) -> None:
        self._registry[class_] = instance

    def allowInterface(self, class_) -> object:
        if class_ in self._registry:
            return self._registry[class_]
        return None

    def createController(self, type_cls) -> Any:
        return self.allowInterface(type_cls)

    def createRepresentation(self, type_cls) -> Any:
        return self.allowInterface(type_cls)

class RepresentationFacroty:
    def createDashboardRepresentation(self, controller: DashboardController) -> IDashboardRepresentation:
        return IDashboardRepresentation(controller)

    def createRecommendationRepresentation(self, controller: RecommendationController) -> IRecommendationRepresentation:
        return IRecommendationRepresentation(controller)

    def createForecastRepresentation(self, controller: ForecastController) -> IForecastRepresentation:
        return IForecastRepresentation(controller)

    def createReportRepresentation(self, controller: ReportController) -> IReportRepresentation:
        return IReportRepresentation(controller)

    def createPortfolioRepresentation(self, controller: PortfolioManagementController) -> IPortfolioRepresentation:
        return IPortfolioRepresentation(controller)

class ControllerFactory:
    def __init__(self, conn):
        self.conn = conn

    def createDashboardController(self) -> DashboardController:
        return DashboardController(DataRepository(self.conn), PortfolioRepository(self.conn))

    def createPortfolioManagementController(self) -> PortfolioManagementController:
        return PortfolioManagementController(PortfolioRepository(self.conn))

    def createAnalysisController(self) -> AnalysisController:
        return AnalysisController(DataRepository(self.conn), [TechnicalAnalysisStrategy(), SentimentAnalysisStrategy()])

    def createForecastController(self) -> ForecastController:
        return ForecastController(ForecastRepository(self.conn), DataRepository(self.conn))

    def createRecommendationController(self) -> RecommendationController:
        return RecommendationController(RecommendationRepository(self.conn))

    def createReportController(self) -> ReportController:
        return ReportController(ReportRepository(self.conn), PortfolioRepository(self.conn), DataRepository(self.conn))
    
    def createAuthController(self) -> AuthController:
        return AuthController(UserRepository(self.conn))
    
    def createAutoTradingController(self) -> AutoTradingController:
        return AutoTradingController(BotRepository(self.conn))
