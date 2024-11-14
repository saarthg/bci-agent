from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model import Response

from crewai_tools import tool

sb = SkillBuilder()

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech_text = "Welcome to your smart home control! You can control your AC, lights, and thermostat."
        
        return handler_input.response_builder\
            .speak(speech_text)\
            .set_should_end_session(False)\
            .response

class TurnOnACIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("TurnOnACIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "Turning on the AC"
        # Here you would add the actual code to control your AC
        
        return handler_input.response_builder\
            .speak(speech_text)\
            .set_should_end_session(True)\
            .response

class TurnOffACIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("TurnOffACIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "Turning off the AC"
        # Here you would add the actual code to control your AC
        
        return handler_input.response_builder\
            .speak(speech_text)\
            .set_should_end_session(True)\
            .response

class TurnOnLightsIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("TurnOnLightsIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "Turning on the lights"
        # Here you would add the actual code to control your lights
        
        return handler_input.response_builder\
            .speak(speech_text)\
            .set_should_end_session(True)\
            .response

class TurnOffLightsIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("TurnOffLightsIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "Turning off the lights"
        # Here you would add the actual code to control your lights
        
        return handler_input.response_builder\
            .speak(speech_text)\
            .set_should_end_session(True)\
            .response

class SetThermostatIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("SetThermostatIntent")(handler_input)

    def handle(self, handler_input):
        # Get the temperature value from the slot
        slots = handler_input.request_envelope.request.intent.slots
        temperature = slots["temperature"].value
        
        speech_text = f"Setting the thermostat to {temperature} degrees"
        # Here you would add the actual code to control your thermostat
        
        return handler_input.response_builder\
            .speak(speech_text)\
            .set_should_end_session(True)\
            .response

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = ("You can say: turn on the AC, turn off the AC, "
                      "turn on the lights, turn off the lights, "
                      "or set the thermostat to a specific temperature.")
        
        return handler_input.response_builder\
            .speak(speech_text)\
            .ask(speech_text)\
            .response

# Add all request handlers to the skill
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(TurnOnACIntentHandler())
sb.add_request_handler(TurnOffACIntentHandler())
sb.add_request_handler(TurnOnLightsIntentHandler())
sb.add_request_handler(TurnOffLightsIntentHandler())
sb.add_request_handler(SetThermostatIntentHandler())
sb.add_request_handler(HelpIntentHandler())

def lambda_handler(event, context):
    return sb.lambda_handler()(event, context)

@tool
def turn_on_ac():
    """This function is used to turn on the AC"""
    test_event = {
        "version": "1.0",
        "request": {
            "type": "IntentRequest",
            "requestId": "amzn1.echo-api.request.12345",
            "intent": {
                "name": "TurnOnACIntent",
                "confirmationStatus": "NONE",
            },
            "locale": "en-US",
            "timestamp": "2024-10-30T10:00:00Z"
        }
    }
    response = lambda_handler(test_event, None)
    return response

@tool
def turn_off_ac():
    """This function is used to turn off the AC"""
    test_event = {
        "version": "1.0",
        "request": {
            "type": "IntentRequest",
            "requestId": "amzn1.echo-api.request.12345",
            "intent": {
                "name": "TurnOffACIntent",
                "confirmationStatus": "NONE",
            },
            "locale": "en-US",
            "timestamp": "2024-10-30T10:00:00Z"
        }
    }
    response = lambda_handler(test_event, None)
    return response

@tool
def turn_on_lights():
    """This function is used to turn on the lights"""
    test_event = {
        "version": "1.0",
        "request": {
            "type": "IntentRequest",
            "requestId": "amzn1.echo-api.request.12345",
            "intent": {
                "name": "TurnOnLightsIntent",
                "confirmationStatus": "NONE",
            },
            "locale": "en-US",
            "timestamp": "2024-10-30T10:00:00Z"
        }
    }
    response = lambda_handler(test_event, None)
    return response

@tool
def turn_off_lights():
    """This function is use to turn off the lights"""
    test_event = {
        "version": "1.0",
        "request": {
            "type": "IntentRequest",
            "requestId": "amzn1.echo-api.request.12345",
            "intent": {
                "name": "TurnOffLightsIntent",
                "confirmationStatus": "NONE",
            },
            "locale": "en-US",
            "timestamp": "2024-10-30T10:00:00Z"
        }
    }
    response = lambda_handler(test_event, None)
    return response

@tool
def set_thermostat(temperature: str):
    "This function takes in a specific temperature and sets the thermostat to that temperature."
    test_event = {
        "version": "1.0",
        "request": {
            "type": "IntentRequest",
            "requestId": "amzn1.echo-api.request.12345",
            "intent": {
                "name": "SetThermostatIntent",
                "confirmationStatus": "NONE",
                "slots": {
                    "temperature": {
                        "name": "temperature",
                        "value": temperature
                    }
                }
            },
            "locale": "en-US",
            "timestamp": "2024-10-30T10:00:00Z"
        }
    }
    response = lambda_handler(test_event, None)
    return response