from flask import Blueprint, jsonify, request
from ai_assistant.ai.enhanced_learning import PersonalKnowledgeGraph
from ai_assistant.ai.active_learning import ActiveLearner

dashboard_api = Blueprint('dashboard_api', __name__)
knowledge_graph = PersonalKnowledgeGraph(db_path="data/knowledge_graph.db")
active_learning = ActiveLearner()

@dashboard_api.route('/api/memory/graph', methods=['GET'])
def get_knowledge_graph():
    """Retrieve the personalized knowledge graph for visualization."""
    try:
        nodes = knowledge_graph.get_all_nodes()
        edges = knowledge_graph.get_all_relationships()
        return jsonify({
            "success": True,
            "nodes": nodes,
            "edges": edges
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@dashboard_api.route('/api/memory/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback for learning and tone adaptation."""
    try:
        data = request.json
        interaction_id = data.get('interaction_id')
        rating = data.get('rating')
        corrections = data.get('corrections', '')
        
        active_learning.log_feedback(interaction_id, rating, corrections)
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@dashboard_api.route('/api/memory/delete', methods=['DELETE'])
def delete_memory_node():
    """Delete a specific fact or preference from memory."""
    try:
        node_id = request.json.get('node_id')
        success = knowledge_graph.delete_node(node_id)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
