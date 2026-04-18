import traceback
import logging
from flask import Blueprint, jsonify, request

from ai_assistant.modules.google_calendar import setup_calendar_auth, get_calendar_service
from ai_assistant.modules.email_handler import setup_email_auth, get_gmail_service

# We wrap in Try/Except since modules might not be fully installed
try:
    from ai_assistant.modules.music import get_spotify_status
    SPOTIFY_LOADED = True
except Exception:
    SPOTIFY_LOADED = False

integrations_bp = Blueprint('integrations_api', __name__)
logger = logging.getLogger(__name__)

@integrations_bp.route('/status', methods=['GET'])
def get_integration_status():
    """Returns the authentication/connection status of all known integrations."""
    try:
        # Check calendar
        calendar_connected = get_calendar_service() is not None
        # Check email
        email_connected = get_gmail_service() is not None
        
        # Check spotify
        spotify_connected = False
        if SPOTIFY_LOADED:
            # We assume it's connected if we don't get an explicit error string containing "❌"
            status = get_spotify_status()
            if "❌" not in str(status) and "Error" not in str(status):
                spotify_connected = True

        return jsonify({
            "success": True,
            "integrations": {
                "google_calendar": {
                    "status": "connected" if calendar_connected else "disconnected"
                },
                "gmail": {
                    "status": "connected" if email_connected else "disconnected"
                },
                "spotify": {
                    "status": "connected" if spotify_connected else "disconnected"
                }
            }
        })
    except Exception as e:
        logger.error(f"Error checking integration status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@integrations_bp.route('/connect', methods=['POST'])
def connect_integration():
    """Trigger the OAuth / connection flow for a specific integration."""
    data = request.json
    integration_id = data.get('integration_id')
    
    try:
        if integration_id == 'google_calendar':
            result = setup_calendar_auth()
            success = "✅" in result
            return jsonify({"success": success, "message": result})
            
        elif integration_id == 'gmail':
            result = setup_email_auth()
            success = "✅" in result
            return jsonify({"success": success, "message": result})
            
        else:
            return jsonify({"success": False, "error": f"Unknown or unsupported integration: {integration_id}"}), 400
            
    except Exception as e:
        logger.error(f"Error connecting {integration_id}: {traceback.format_exc()}")
        return jsonify({"success": False, "error": str(e)}), 500

# ==========================================
# MCP (Model Context Protocol) Endpoints
# ==========================================

@integrations_bp.route('/mcp', methods=['GET'])
def get_mcp_status():
    """Returns the status of configured MCP servers and their available tools."""
    try:
        import asyncio
        from ai_assistant.integrations.mcp_manager import get_mcp_manager
        
        # We need an event loop for async functions
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        manager = loop.run_until_complete(get_mcp_manager())
        status = manager.get_status()
        all_tools = loop.run_until_complete(manager.get_all_tools())
        
        # Also need access to client to get detailed server info
        if hasattr(manager, 'client') and manager.client:
            all_servers = manager.client.get_all_servers()
        else:
            all_servers = []
            # Fallback if client isn't fully ready
            for srv_name, srv_config in manager.config.get('servers', {}).items():
                all_servers.append({
                    "name": srv_name,
                    "description": srv_config.get("description", f"MCP Server: {srv_name}"),
                    "connected": srv_name in manager.enabled_servers,
                    "enabled": srv_config.get("enabled", True)
                })

        # Format for UI
        servers_response = []
        for server_info in all_servers:
            name = server_info.get("name")
            servers_response.append({
                "id": f"mcp_{name}",
                "name": name.title().replace("-", " "),
                "description": server_info.get("description", f"MCP Server: {name}"),
                "status": "connected" if server_info.get("connected") else ("error" if name in manager.failed_servers else "disconnected"),
                "category": "MCP",
                "isEnabled": server_info.get("enabled", True),
                "tools": all_tools.get(name, [])
            })
            
        loop.close()
            
        return jsonify({
            "success": True,
            "status": status,
            "servers": servers_response
        })
    except Exception as e:
        logger.error(f"Error getting MCP status: {traceback.format_exc()}")
        return jsonify({"success": False, "error": str(e)}), 500

@integrations_bp.route('/mcp/reload', methods=['POST'])
def reload_mcp():
    """Reloads the MCP configuration and reconnects servers."""
    try:
        import asyncio
        from ai_assistant.integrations.mcp_manager import get_mcp_manager
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        manager = loop.run_until_complete(get_mcp_manager())
        loop.run_until_complete(manager.reload_config())
        
        loop.close()
        
        return jsonify({"success": True, "message": "MCP configuration reloaded!"})
    except Exception as e:
        logger.error(f"Error reloading MCP: {traceback.format_exc()}")
        return jsonify({"success": False, "error": str(e)}), 500
