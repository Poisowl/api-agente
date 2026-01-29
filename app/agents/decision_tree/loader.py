import json
from pathlib import Path

flows_path = Path("assets/flow")

def load_flow(flow_id: str) -> dict :
    path = flows_path / f"{flow_id}.json"
    if not path.exists():
        raise ValueError(F"Flow {flow_id} no existe")
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)