from fbusl.node import *


class Injector:
    def __init__(self, tree: list[ASTNode]):
        self.tree = tree

    def inject(self):
        return self.tree
