import string
from typing import List

from infrastructure import DependencyContainer
from model import Repository
from representation import IRepresentation

#main
#использует все имеющиеся контроллеры
class Application:
    def main(self, args: List[str]) -> None:
        pass

    def __init__(self) -> None:
        pass

#interface
class IController:
    pass

#injector
#настраивает DependencyContainer
class SystemConfigurator:
    def configureDependencies(self, container: DependencyContainer) -> None:
        pass

    def createRepositories(self) -> List[Repository]:
        pass

    def createControllers(self, repositories: List) -> List[IController]:
        pass

    def createRepresentations(self, controllers: List) -> List[IRepresentation]:
        pass

    def linkComponents(self) -> None:
        pass

if __name__ == "__main__":
    main = Application()



