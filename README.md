# Speech Neuroprosthesis-native Personal Assistant

## Getting Started

To get started with this framework, follow these steps:

1. **Clone the Repository**: Clone the repository locally using the following command:
    ```bash
    git clone <repository-url>
    ```

2. **Set Up Virtual Environment**: Set up a virtual Python environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies**: Install the necessary dependencies listed in the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

4. **Create OpenAI API Key**: Create an OpenAI API key and paste it into the `.env` file.

5. **Run the Application**: To test the framework, run the following command in the terminal:
    ```bash
    python app.py
    ```
    You will then be prompted to enter your query, and the agent workflow will be executed.

## Customizing the Framework

### Outer Planning Agent

The initial code includes the outer planning agent, as well as the SmartHome agent and the browser agent.

### Customizing Tools

To customize tools, you can directly edit the tools listed in the SmartHome and browser agent files. You can also add new tools by creating a new function with the CrewAI `@Tool` decorator.

### Adding New Inner Agents

To add a new inner agent, follow the template for the other inner agents. You will need to specify the agent's role, its goal, its backstory, and its LLM. Make sure to also add relevant tools specific to your agent, including the ask for user input and verification tools.

After adding a new inner agent, you will need to create a tool that calls the agent (refer to the call smart home agent tool in `app.py`). Then, add this tool to the planning agent's set of tools. Thus, with this framework, you can easily customize and add inner agents or tools as necessary.

## Response Generator

The response generation module will also need to run in parallel with the other agent. The requirements for this component are already installed in the first section. To run this module, simply run the `mc_response.py` file and allow microphone access:
```bash
python mc_response.py
```
