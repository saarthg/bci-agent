from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model import Response

from crewai_tools import tool
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

import os
import sys
from dotenv import load_dotenv

from gmail import gmail_create_draft
from mc_response import choose_response
from smarthome import set_thermostat, turn_off_ac, turn_off_lights, turn_on_ac, turn_on_lights

load_dotenv()

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
    if user_input.lower() == "no":
        return "Task execution aborted."
    expanded_query = expand_user_query(user_input)
    return expanded_query


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
    if result == "Task execution aborted.":
        print("No further action will be taken.")
        return result
    return result

@tool
def call_email_agent(query: str):
    """This function calls the email agent, which can execute tasks like sending emails, drafting emails, etc. 
    The function takes in the user query that needs to be executed."""
    task = Task(
        description=f'Execute the following user query: {query}',
        agent=emailAgent,
        expected_output='A message of confirmation that the task has been executed.',
    )
    crew = Crew(
        agents=[emailAgent],
        tasks=[task],
        verbose=True
    )
    result = crew.kickoff()
    return result

llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=os.getenv("OPENAI_API_KEY"))

if __name__ == "__main__":
    smartHomeAgent = Agent(
        role='Smart Home Agent',
        goal='Execute the user query to control smart home devices. Make sure to ask for confirmation before calling tools.',
        backstory="""You are a smart home agent capable of controlling smart home devices such as the AC,
        thermostat, lights, etc.""",
        tools=[turn_on_ac, turn_off_ac, turn_off_lights, turn_on_lights, set_thermostat, ask_for_user_input, expand_user_query, verify_with_user],
        llm=llm,
        verbose=True
    )

    planningAgent = Agent(
        role='Planning Agent',
        goal='Execute the user query and decide which agents to call',
        backstory="""You are the outer planning agent, responsible for understanding the user query and sending relevant information
        to the appropriate agents.""",
        llm=llm,
        tools=[call_smart_home_agent, call_email_agent, expand_user_query, choose_response],
        verbose=True
    )

    emailAgent = Agent(
        role='Email Agent',
        goal='Execute the user query to manage their email. Make sure to ask for confirmation before calling tools.',
        backstory='You are an email agent capable of managing email tasks such as sending emails, drafting emails, etc.',
        llm=llm,
        tools=[gmail_create_draft, ask_for_user_input, expand_user_query, verify_with_user],
        verbose=True
    )

    # response_agent = Agent(
    #     role='Response Agent',
    #     goal='Helps the user respond to incoming questions',
    #     backstory='You are a response agent helping the user respond to incoming questions.',
    #     llm=llm,
    #     tools=[choose_response],
    #     verbose=True
    # )
    
    while True:
        user_input = input("Enter your query: ").strip()
        expanded_input = expand_user_query.run(user_input)

        task = Task(
            description=f'Execute the following user query: {expanded_input}',
            agent=planningAgent,
            expected_output='A message of confirmation that the task has been executed.',
        )

        crew = Crew(
            agents=[planningAgent],
            tasks=[task],
            verbose=True
        )

        result = crew.kickoff()

        if "Task execution aborted." in result:
            print("No further action will be taken for this query.")
            continue
        elif isinstance(result, str) and result.startswith("only"):
            print(f"Updating task to new context: {result}")
            updated_task = Task(
                description=f'Execute the following user query: {result}',
                agent=planningAgent,
                expected_output='A message of confirmation that the task has been executed.',
            )
            updated_crew = Crew(
                agents=[planningAgent],
                tasks=[updated_task],
                verbose=True
            )
            updated_result = updated_crew.kickoff()
            print(updated_result)
        else:
            print("Task completed.")
            break

