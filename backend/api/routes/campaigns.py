from fastapi import APIRouter
import uuid
import random

router = APIRouter()

@router.get("/detected")
async def get_detected_campaigns():
    """
    Returns detected bot networks and influence campaigns as a Graph (Nodes & Edges).
    In production, this queries the Neo4j database using Cypher.
    """
    # Generate a mock bot network graph
    nodes = []
    links = []
    
    # Core command nodes
    core_id = str(uuid.uuid4())
    nodes.append({"id": core_id, "group": "Command", "radius": 20, "color": "#f43f5e"}) # Rose-500
    
    # Sub-controllers
    sub_nodes = [str(uuid.uuid4()) for _ in range(3)]
    for sub_id in sub_nodes:
        nodes.append({"id": sub_id, "group": "Controller", "radius": 15, "color": "#fb923c"}) # Orange-400
        links.append({"source": core_id, "target": sub_id, "value": 5})
        
    # Amplifier bots
    for sub_id in sub_nodes:
        for _ in range(random.randint(5, 12)):
            bot_id = str(uuid.uuid4())
            nodes.append({"id": bot_id, "group": "Amplifier", "radius": 8, "color": "#38bdf8"}) # Sky-400
            links.append({"source": sub_id, "target": bot_id, "value": 1})
            
            # Add some dense interlinking representing coordinated retweets
            if random.random() > 0.8 and len(nodes) > 10:
                random_target = nodes[-random.randint(1, 10)]["id"]
                links.append({"source": bot_id, "target": random_target, "value": 1})

    return {
        "status": "success",
        "campaign_name": "Op_SilentEcho",
        "metrics": {
            "total_nodes": len(nodes),
            "total_edges": len(links),
            "threat_level": "High"
        },
        "graph_data": {
            "nodes": nodes,
            "links": links
        }
    }
