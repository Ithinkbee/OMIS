import sqlite3
from typing import List

from infrastructure import DependencyContainer, ControllerFactory, RepresentationFactory
from model import Repository, DataRepository, UserRepository
from representation import MainWindow
from database_setup import DatabaseSetup

class SystemConfigurator:
    def __init__(self, db_name="finance_platform.db"):
        self.db_name = db_name

    def configureDependencies(self, container: DependencyContainer, factory: ControllerFactory, rep_factory: RepresentationFactory) -> dict:
        ctrls = {
            'auth': factory.createAuthController(),
            'dash': factory.createDashboardController(),
            'forecast': factory.createForecastController(),
            'rec': factory.createRecommendationController(),
            'rep': factory.createReportController(),
            'port': factory.createPortfolioManagementController(),
            'bot': factory.createAutoTradingController(),
            'analysis': factory.createAnalysisController()
        }
        
        for name, instance in ctrls.items():
            container.registerInterface(name, instance)
            
        reps = {
            'dash': rep_factory.createDashboardRepresentation(ctrls['dash']),
            'rec': rep_factory.createRecommendationRepresentation(ctrls['rec']),
            'forecast': rep_factory.createForecastRepresentation(ctrls['forecast']),
            'rep': rep_factory.createReportRepresentation(ctrls['rep']),
            'port': rep_factory.createPortfolioRepresentation(ctrls['port'])
        }
        
        for name, instance in reps.items():
            container.registerInterface(f"rep_{name}", instance)
            
        return ctrls, reps

    def linkComponents(self) -> None:
        print("System linked and ready.")

class Application:
    def __init__(self) -> None:
        self.configurator = SystemConfigurator()
        self.container = DependencyContainer()

    def main(self, args: List[str]) -> None:
        db_setup = DatabaseSetup()
        db_setup.initialize_db()
        
        conn = sqlite3.connect("finance_platform.db", check_same_thread=False)
        
        ctrl_factory = ControllerFactory(conn)
        rep_factory = RepresentationFactory()
        
        ctrls, reps = self.configurator.configureDependencies(self.container, ctrl_factory, rep_factory)
        self.configurator.linkComponents()
        
        app = MainWindow(ctrls, reps)
        app.mainloop()

if __name__ == "__main__":
    main_app = Application()
    main_app.main([])