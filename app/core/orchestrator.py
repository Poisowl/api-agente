from app.agents.decision_tree.agent import DecisionTreeAgent


class Orchestrator:
    def handle(self, payload):
        # por ahora solo árbol
        agent = DecisionTreeAgent()
        return agent.process(payload)
