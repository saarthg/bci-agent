from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model import Response

from crewai_tools import tool

tracked_calls = []
def track_call(tool_name: str, *args):
    tracked_calls.append((tool_name, args))

@tool
def turn_on_ac():
    """This function is used to turn on the AC"""
    track_call("turn_on_ac")
    return "AC turned on."

@tool
def turn_off_ac():
    """This function is used to turn off the AC"""
    track_call("turn_off_ac")
    return "AC turned off."

@tool
def turn_on_lights():
    """This function is used to turn the lights on"""
    track_call("turn_on_lights")
    return "Lights turned on."

@tool
def turn_off_lights():
    """This function is used to turn the lights off"""
    track_call("turn_off_lights")
    return "Lights turned off."

@tool
def set_thermostat(temperature: str):
    """This function takes in a specific temperature and sets the thermostat to that temperature."""
    track_call("set_thermostat", temperature)
    return f"Thermostat set to {temperature} degrees."

@tool
def adjust_curtains(state: str):
    """This function adjusts curtains or blinds. Takes in the state 'open' or 'close'."""
    track_call("adjust_curtains", state)
    return f"Curtains {state}."

@tool
def start_appliance(appliance: str):
    """This function starts a specific home appliance, e.g., dishwasher, laundry."""
    track_call("start_appliance", appliance)
    return f"{appliance.capitalize()} started."

@tool
def stop_appliance(appliance: str):
    """This function stops a specific home appliance, e.g., dishwasher, laundry."""
    track_call("stop_appliance", appliance)
    return f"{appliance.capitalize()} stopped."

@tool
def manage_security(action: str):
    """This function manages the home security system, including cameras and alarms. Actions could include 'arm', 'disarm', or 'monitor'."""
    track_call("manage_security", action)
    return f"Security system {action}."

@tool
def manage_locks(lock_state: str):
    """This function manages door locks. Takes in 'lock' or 'unlock'."""
    track_call("manage_locks", lock_state)
    return f"Doors {lock_state}."

@tool
def answer_video_doorbell():
    """This function simulates answering a video doorbell."""
    track_call("answer_video_doorbell")
    return "Video doorbell answered."

@tool
def control_entertainment_device(device: str, action: str):
    """This function controls entertainment devices like TVs or speakers. 
    Takes in the device (e.g., 'TV') and action (e.g., 'on', 'off')."""
    track_call("control_entertainment_device", device, action)
    return f"{device.capitalize()} turned {action}."

@tool
def search_and_play_content(content: str):
    """This function searches for and plays specific content (e.g., a song or movie)."""
    track_call("search_and_play_content", content)
    return f"Playing {content}."

@tool
def control_streaming_service(service: str, action: str):
    """This function controls streaming services. Takes in the service name and action (e.g., 'play', 'pause')."""
    track_call("control_streaming_service", service, action)
    return f"{action.capitalize()} on {service}."

