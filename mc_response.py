from langchain_core.tools import tool
from langchain_openai import ChatOpenAI


@tool
def choose_response(question: str) -> str:
    """
    This function should be called when a question or comment is posed to this system's user. 
    
    Args:
        question (str): The question or comment posed to the user.
    Returns:
        str: The chosen or user-inputted response.
    """
    # Generate possible responses using OpenAI
    llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=os.getenv("OPENAI_API_KEY"))
    response = llm.invoke(
        engine="text-davinci-003",
        prompt=f"Generate multiple choice responses for the following question:\n\n{question}\n\nResponses:",
        max_tokens=150,
        n=4,
        stop=None,
        temperature=0.7
    )

    # Extract the generated responses
    choices = [choice['text'].strip() for choice in response.choices]
    choices.append("None of the above")

    # Present the choices to the user
    print("Please choose a response:")
    for i, choice in enumerate(choices):
        print(f"{i + 1}. {choice}")

    # Get the user's choice
    user_choice = int(input("Enter the number of your choice: ")) - 1

    # If the user selects "None of the above", prompt for their own response
    if user_choice == len(choices) - 1:
        user_response = input("Please enter your response: ")
    else:
        user_response = choices[user_choice]

    # Return the chosen or user-inputted response
    return user_response
