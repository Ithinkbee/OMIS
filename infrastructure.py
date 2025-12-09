from pyclbr import Class
from typing import List
from control import AnalysisController, DashboardController, ForecastController, PortfolioManagementController, RecommendationController, ReportController
from representation import IDashboardRepresentation, IForecastRepresentation, IPortfolioRepresentation, IRecommendationRepresentation, IReportRepresentation

#injector
#создаёт Repository 
class DependencyContainer:
    def registerInterface(self, class_, realization) -> None:
        pass

    def allowInterface(self, class_) -> object:
        pass

    def createController(self, type) -> Class:
        pass

    def createRepresentation(self, type) -> Class:
        pass

#injector
class RepresentationFacroty:
    def createDashboardRepresentation(self, controller: DashboardController) -> IDashboardRepresentation:
        pass

    def createRecommendationRepresentation(self, controller: RecommendationController) -> IRecommendationRepresentation:
        pass

    def createForecastRepresentation(self, controller: ForecastController) -> IForecastRepresentation:
        pass

    def createReportRepresentation(self, controller: ReportController) -> IReportRepresentation:
        pass

    def createPortfolioRepresentation(self, controller: PortfolioManagementController) -> IPortfolioRepresentation:
        pass

#injector
class ControllerFactory:
    def createDashboardController(self, repositories: List) -> DashboardController:
        pass

    def createPortfolioManagementController(self, repositories: List) -> PortfolioManagementController:
        pass

    def createAnalysisController(self, repositories: List, strategies: List) -> AnalysisController:
        pass

    def createForecastController(self, repositories: List) -> ForecastController:
        pass

    def createRecommendationController(self, repositories: List) -> RecommendationController:
        pass

    def createReportController(self, repositories: List) -> ReportController:
        pass

    
