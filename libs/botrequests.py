from .data import Settings
import requests

discord_api_endpoint = "https://discord.com/api/v9/interactions"
application_id = "936929561302675456"
version = "1077969938624553050"
id = "938956540159881230"

def SimulatePrompt(prompt : str, channel_id: str, settings: Settings):
    data = {
    "type": 2,
    "data": {
        "version": version,
        "id": id,
        "name": "imagine",
        "type": 1,
        "options": [{
            "type":3,
            "name":"prompt",
            "value":prompt
            }],
        "application_command": {
            "id": id,
            "application_id": application_id,
            "version": version,
            "default_permission": "true",
            "default_member_permissions": "None",
            "type": 1,
            "nsfw": "false",
            "name": "imagine",
            "description": "Create images with Midjourney",
            "dm_permission": "true",
            "options": [{
                "type": 3,
                "name": "prompt",
                "description": "The prompt to imagine",
                "required": "true"
                }]
            },
            "attachments": []
        },
    
        "guild_id": settings.server_id,
        "channel_id": channel_id,

        "application_id": application_id,
        "session_id": "2fb980f65e5c9a77c96ca01f2c242cf6"
        }

    headers = {
        'authorization' : settings.relay_token
    }
    return requests.post(discord_api_endpoint, json = data, headers = headers)

def SimulateUpscale(index : int, messageId, hash : str, channel_id, settings: Settings):
    custom_id = f"MJ::JOB::upsample::{index}::{hash}"
    data = {
        "type": 3,
        "data": {
            "component_type": 2,
            "custom_id": custom_id
        },

        "guild_id": settings.server_id,
        "channel_id": channel_id,
        "message_id": messageId,
       
        "message_flags": 0,
        "application_id": application_id,
        "session_id": "45bc04dd4da37141a5f73dfbfaf5bdcf"
    }
    
    headers = {
        'authorization' : settings.relay_token
    }

    return requests.post(discord_api_endpoint, json = data, headers = headers)


  
