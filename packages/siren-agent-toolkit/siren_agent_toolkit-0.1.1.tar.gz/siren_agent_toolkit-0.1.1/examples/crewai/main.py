"""Example of using Siren Agent Toolkit with CrewAI."""

import os
from dotenv import load_dotenv
load_dotenv()
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from agenttoolkit.crewai import SirenAgentToolkit


def main():

    llm = ChatOpenAI(
        model="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    

    siren_toolkit = SirenAgentToolkit(
        api_key=os.getenv("SIREN_API_KEY"),
        configuration={
            "actions": {
                "messaging": {
                    "create": True,
                    "read": True,
                },
                "templates": {
                    "read": True,
                    "create": True,
                    "update": True,
                    "delete": True,
                },
                "users": {
                    "create": True,
                    "update": True,
                    "delete": True,
                    "read": True,
                },
                "workflows": {
                    "trigger": True,
                    "schedule": True,
                },
            },
        },
    )
    

    notification_agent = Agent(
        role="Notification Manager",
        goal="Send notifications and manage notification templates using Siren",
        backstory="You are an expert at managing notifications and templates. You can send messages, create templates, and manage users through the Siren platform.",
        tools=siren_toolkit.get_tools(),
        llm=llm,
        verbose=True,
    )
    

    send_welcome_task = Task(
        description='send welcome message, "Welcome to our service!" to user@example.com via EMAIL',
        agent=notification_agent,
        expected_output="confirm it returns request id and workflowExecutionId",
    )
    

    crew = Crew(
        agents=[notification_agent],
        tasks=[send_welcome_task],
        verbose=True,
    )
    

    result = crew.kickoff()
    print(f"Result: {result}")


if __name__ == "__main__":
    main()