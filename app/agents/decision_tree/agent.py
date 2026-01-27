from app.core.engine import DecisionTreeEngine


class DecisionTreeAgent:

    def process(self, payload):
        engine = DecisionTreeEngine()
        return engine.run(payload)