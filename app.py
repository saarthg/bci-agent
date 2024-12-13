from crewai_tools import tool
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

import os
import sys
import logging
from dotenv import load_dotenv

from computerAgent import book_ride, browse_and_purchase_items, enable_navigation_and_multiapp, file_operations, fill_online_form, gmail_create_draft, manage_emails, manage_messages, manage_social_media, navigate_links_or_menus, order_groceries, perform_online_banking, public_transit_schedule, schedule_meeting, search_files, speech_based_search
from smartHomeAgent import adjust_curtains, answer_video_doorbell, control_entertainment_device, control_streaming_service, manage_locks, manage_security, search_and_play_content, set_thermostat, start_appliance, stop_appliance, turn_off_ac, turn_off_lights, turn_on_ac, turn_on_lights
from browser_control import browser_control
from browser_control import BrowserControl

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

browser_controller = BrowserControl()

@tool
def send_friend_email(message: str):
    """Sends an email to the hardcoded friend's address with a dynamic message"""
    try:
        logger.info(f"Attempting to send email with message: {message}")
        
        success = browser_controller.switch_to_tab("gmail")
        if not success:
            return "Failed to access Gmail"
        
        recipient = "emailypark@gmail.com"  # hardcoded email
        subject = "Message from Friend"
        
        if browser_controller.compose_email(recipient, subject, message):
            return "Successfully sent email"
        return "Failed to send email"
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return f"Error: {str(e)}"

@tool
def call_browser_agent(query: str):
    """This function calls the browser agent, which can execute tasks like switching tabs and navigation."""
    task = Task(
        description=f'Execute the following user query: {query}',
        agent=browserAgent,
        expected_output='A message of confirmation that the task has been executed.',
    )
    crew = Crew(
        agents=[browserAgent],
        tasks=[task],
        verbose=True
    )
    result = crew.kickoff()
    return result

@tool
def expand_user_query(query: str) -> str:
    """This function takes a short user query and expands it into a detailed, task-oriented request for automation purposes."""
    prompt = (
        f"The user said: '{query}'. "
        "Please expand this into a detailed and actionable request from this word to a sentence to initiate the next automation task flow."
    )
    response = llm.invoke(prompt)
    return response.content

@tool
def ask_for_user_input(question: str):
    """This function asks for additional user input if there is not enough information. Takes in a question to ask the user."""
    user_input = input(question)
    return user_input


@tool 
def verify_with_user(confirmation: str) -> str:
    """Verifies with the user if they want to execute a task.
    If the user says no, it captures their additional instructions or ends the task."""
    user_input = input(f"{confirmation} (yes/no or provide additional instructions): ").strip().lower()
    
    if user_input in ["no", "nope", "n"]:
        print("User declined the task.")
        return "Task execution aborted."
    elif user_input.startswith("no "): # provides addition info after 'no'
        print("Captured additional instructions from user.")
        return user_input[3:].strip()  # return only the new instructions after "no "
    elif user_input in ["yes", "y"]:
        return "User confirmed."
    else:
        print("Invalid response. Assuming 'no'.")
        return "Task execution aborted."

@tool
def call_smart_home_agent(query: str):
    """This function calls the Smart Home agent, which can execute tasks like turning on the AC, setting the thermostat, etc.
    The function takes in the user query that needs to be executed."""
    task = Task(
        description=f'Execute the following user query: {query}',
        agent=smartHomeAgent,
        expected_output='A message of confirmation that the task has been executed.',
    )
    crew = Crew(
        agents=[smartHomeAgent],
        tasks=[task],
        verbose=True
    )
    result = crew.kickoff()
    return result

@tool
def call_computer_agent(query: str):
    """This function calls the email agent, which can execute tasks like sending emails, drafting emails, etc. 
    The function takes in the user query that needs to be executed."""
    task = Task(
        description=f'Execute the following user query: {query}',
        agent=computerAgent,
        expected_output='A message of confirmation that the task has been executed.',
    )
    crew = Crew(
        agents=[computerAgent],
        tasks=[task],
        verbose=True
    )
    result = crew.kickoff()
    return result

llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=os.getenv("OPENAI_API_KEY"))

verification = "Make sure to ask for confirmation before calling tools." #Have removed this from the agent prompts for now due to testing

smartHomeAgent = Agent(
    role='Smart Home Agent',
    goal='Execute the user query to control smart home devices.',
    backstory="""You are a smart home agent capable of controlling smart home devices such as the AC,
    thermostat, lights, etc.""",
    tools=[turn_on_ac, turn_off_ac, turn_off_lights, turn_on_lights, 
            set_thermostat, adjust_curtains, start_appliance, stop_appliance, 
            manage_security, manage_locks, answer_video_doorbell, control_entertainment_device, 
            search_and_play_content, control_streaming_service, ask_for_user_input, verify_with_user],
    llm=llm,
    verbose=True
)

planningAgent = Agent(
    role='Planning Agent',
    goal='Execute the user query and decide which agents to call',
    backstory="""You are the outer planning agent, responsible for understanding the user query and sending relevant information
    to the appropriate agents.""",
    llm=llm,
    tools=[call_smart_home_agent, call_computer_agent, call_browser_agent],
    verbose=True
)

computerAgent = Agent(
    role='Computer Agent',
    goal='Execute the user query.',
    backstory='You are a computer agent capable of managing emails/messages, navigating apps, ordering rides, etc.',
    llm=llm,
    tools=[
        gmail_create_draft, speech_based_search,navigate_links_or_menus, manage_emails,
        search_files, enable_navigation_and_multiapp, file_operations, manage_messages, manage_social_media,
        schedule_meeting, perform_online_banking, browse_and_purchase_items,
        order_groceries, book_ride, public_transit_schedule, fill_online_form, 
        ask_for_user_input, verify_with_user
    ],
    verbose=True
)

browserAgent = Agent(
        role='Browser Control Agent',
        goal='Execute browser-related commands like switching tabs and navigation',
        backstory="""You are a browser control agent capable of managing browser windows,
        tabs, and navigation.""",
        tools=[browser_control, ask_for_user_input, expand_user_query, verify_with_user],
        llm=llm,
        verbose=True
)

def execute_query(user_input):
    if user_input.lower().startswith("mail friend"):
        logger.info("Detected friend email request")
        message = user_input[11:].strip()  # length of "mail friend "
        if message:
            return send_friend_email.run(message)  # .run() to execute the tool
        else:
            return "No message provided for the email"
    
    task = Task(
        description=f'Execute the following user query: {user_input}',
        agent=planningAgent,
        expected_output='A message of confirmation that the task has been executed.',
    )

    crew = Crew(
        agents=[planningAgent],
        tasks=[task],
        verbose=True
    )

    result = crew.kickoff()
    return result

if __name__ == "__main__":
    user_input = input("Enter your query: ").strip()
    #expanded_input = expand_user_query.run(user_input)
    execute_query(user_input)
    
    
    # while True:
    #     user_input = input("Enter your query: ").strip()
    #     expanded_input = expand_user_query.run(user_input)

    #     task = Task(
    #         description=f'Execute the following user query: {expanded_input}',
    #         agent=planningAgent,
    #         expected_output='A message of confirmation that the task has been executed.',
    #     )

    #     crew = Crew(
    #         agents=[planningAgent],
    #         tasks=[task],
    #         verbose=True
    #     )

    #     result = crew.kickoff()

    #     if "Task execution aborted." in result:
    #         print("No further action will be taken for this query.")
    #         continue
    #     elif isinstance(result, str) and result.startswith("only"):
    #         print(f"Updating task to new context: {result}")
    #         updated_task = Task(
    #             description=f'Execute the following user query: {result}',
    #             agent=planningAgent,
    #             expected_output='A message of confirmation that the task has been executed.',
    #         )
    #         updated_crew = Crew(
    #             agents=[planningAgent],
    #             tasks=[updated_task],
    #             verbose=True
    #         )
    #         updated_result = updated_crew.kickoff()
    #         print(updated_result)
    #     else:
    #         print("Task completed.")
    #         break

