__author__ = 'Owner'

import settings


class Component:
    def __init__(self, name, isMobile, connectTo_name, connectTo_isMobile):
        self.name = name
        self.isMobile = isMobile
        self.connectTo_name = connectTo_name
        self.connectTo_isMobile = connectTo_isMobile

# class DAG:
    # def __init__(self):
    #     self.relationships = []

    # def connect(self, component1, component2):
    #     self.relationships[component1] = component2


def parse_game_dag(game_dag):
    # dagObj = DAG()
    dagObj = []
    # dag = settings.game_dag.get(game_name)
    if game_dag is not None:
        relationships = game_dag.split(',')
        for r in relationships:
            components = r.split(':')
            # C2 = Component(components[1][0], components[1][1])
            C1 = Component(components[0][0], components[0][1], components[1][0], components[1][1])

            # dagObj.connect(C1, C2)
            dagObj.append(C1)
    return dagObj

