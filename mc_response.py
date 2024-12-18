from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import speech_recognition as sr

class ResponseChoice(BaseModel):
    """Model for a single response choice"""
    id: int = Field(description="Unique identifier for the response choice")
    text: str = Field(description="The actual response text")
    source: str = Field(description="Source of the response - either 'ai' or 'user'")

class ResponseOutput(BaseModel):
    """Model for the complete response output"""
    original_question: str = Field(description="The original question that was asked")
    choices: List[ResponseChoice] = Field(description="List of all response choices presented")
    selected_choice: ResponseChoice = Field(description="The final selected response")
    user_input_required: bool = Field(description="Whether user input was required")

@tool
def choose_response(question: str) -> ResponseOutput:
    """
    This function processes a question and returns structured response choices.
    
    Args:
        question (str): The question or comment posed to the user.
    Returns:
        ResponseOutput: A structured output containing all response data.
    """
    # Generate possible responses using OpenAI
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        max_tokens=150,
        temperature=0.7,
        verbose=True
    )
    
    # Updated prompt to be more explicit about the required format
    response = llm.invoke(
        input=f"""Generate 4 appropriate response choices for this question: "{question}"
        Note that this question is being posed to a user living with paralysis, so generated answers should take into account how they may want to respond. 
        Also, ensure that responses are different, and cover a range of possible reactions.
        
        Return them in this exact JSON format:
        {{
            "choices": [
                {{"text": "first response"}},
                {{"text": "second response"}},
                {{"text": "third response"}},
                {{"text": "fourth response"}}
            ]
        }}""",
        response_format={"type": "json_object"}
    )
    
    # Add debug logging
    print(f"Raw LLM response: {response.content}")
    
    # Parse the response and create structured choices
    try:
        import json
        choices_data = json.loads(response.content)
        
        # Extract the choices array
        choices_list = choices_data.get('choices', [])
        print(f"Parsed choices: {choices_list}")
        
        ai_choices = [
            ResponseChoice(
                id=i,
                text=choice['text'],
                source='ai'
            ) for i, choice in enumerate(choices_list)
        ]
        
        if not ai_choices:
            raise ValueError("No choices were generated")
            
    except Exception as e:
        print(f"Error parsing LLM response: {str(e)}")
        # Provide fallback choices if parsing fails
        ai_choices = [
            ResponseChoice(
                id=0,
                text="Yes",
                source='fallback'
            ),
            ResponseChoice(
                id=1,
                text="No",
                source='fallback'
            )
        ]
    
    # Add "None of the above" option
    none_choice = ResponseChoice(
        id=len(ai_choices),
        text="None of the above",
        source='system'
    )
    all_choices = ai_choices + [none_choice]

    # Present the choices to the user
    print("\nPlease choose a response:")
    for choice in all_choices:
        print(f"{choice.id + 1}. {choice.text}")

    # Get the user's choice
    while True:
        try:
            user_choice = int(input("\nEnter the number of your choice: ")) - 1
            if 0 <= user_choice < len(all_choices):
                break
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

    user_input_required = user_choice == len(all_choices) - 1

    # Handle user input if needed
    if user_input_required:
        user_text = input("Please type your desired response: ")
        llm_response = llm.invoke(
            input=f"""Rewrite the following input to be a complete informal sentence response to the original question:
            
            Original Question: "{question}"
            User Input: "{user_text}"
            
            Response should be a single informal sentence.""",
            response_format={"type": "text"}
        )
        
        user_text = llm_response.content.strip()
        selected_choice = ResponseChoice(
            id=len(all_choices),
            text=user_text,
            source='user'
        )
    else:
        selected_choice = all_choices[user_choice]

    # Create and return the structured output
    return ResponseOutput(
        original_question=question,
        choices=all_choices,
        selected_choice=selected_choice,
        user_input_required=user_input_required
    )

class QuestionValidationResult(BaseModel):
    """Model for question validation results"""
    is_valid: bool = Field(description="Whether the input is a valid question")
    confidence_score: float = Field(description="Confidence score of the validation")
    question: Optional[str] = Field(None, description="Cleaned question text if valid")
    error_message: Optional[str] = Field(None, description="Error message if validation fails")

def is_valid_question(question: str) -> QuestionValidationResult:
    """
    This function validates if the input is a valid question or comment using an LLM.
    
    Args:
        question (str): The input to validate.
    Returns:
        QuestionValidationResult: Structured validation results.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        max_tokens=50,
        temperature=0.1,
        verbose=True,    
    )
    
    response = llm.invoke(
        input=f"""Analyze if the following input is a valid question or comment that could be posed to a user.
        
        Input: {question}
        
        Response should include:
        - is_valid: boolean indicating if it's a valid question
        - confidence_score: number between 0 and 1
        - question: if question is valid, the cleaned question text (optional if not valid)
        - error_message: optional string explaining why it's invalid
        
        Response must be in the form of a JSON object.""",
        response_format={"type": "json_object"},
    )
    
    # Parse the LLM response into structured format
    try:
        # Use json.loads instead of eval for safer parsing
        import json
        result_dict = json.loads(response.content)
        return QuestionValidationResult(**result_dict)
    except Exception as e:
        print(f"Error parsing validation result: {str(e)}")
        print(f"Raw response: {response.content}")
        return QuestionValidationResult(
            is_valid=False,
            confidence_score=0.0,
            error_message=f"Error parsing validation result: {str(e)}"
        )

def listen_for_question() -> Optional[str]:
    """
    Listen for audio input and convert it to text.
    
    Returns:
        Optional[str]: The transcribed question or None if unsuccessful
    """
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Listening for a question...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        question = recognizer.recognize_google(audio)
        print(f"Question heard: {question}")
        validation_result = is_valid_question(question)
        
        if not validation_result.is_valid:
            print(f"Invalid input: {validation_result.error_message}")
            return None
            
        return validation_result.question
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError:
        print("Could not request results from Google Speech Recognition service.")
        return None

if __name__ == "__main__":
    while True:
        question = listen_for_question()
        if question:
            response_output = choose_response.invoke(question)
            print("\nResponse Summary:")
            print(f"Original Question: {response_output.original_question}")
            print(f"Selected Response: {response_output.selected_choice.text}")
            print(f"Response Source: {response_output.selected_choice.source}")
            if response_output.user_input_required:
                print("Custom user input was provided")