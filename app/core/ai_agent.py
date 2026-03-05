from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults

from langgraph.prebuilt import create_react_agent
from langchain_core.messages.ai import AIMessage

from app.config.settings import settings

def get_response_from_ai_agents(llm_id , query , allow_search ,system_prompt):
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not configured")

    if allow_search and not settings.TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY is required when web search is enabled")

    llm = ChatGroq(model=llm_id)

    tools = [TavilySearchResults(max_results=2)] if allow_search else []

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt
    )

    state = {"messages" : query}

    response = agent.invoke(state)

    messages = response.get("messages")

    ai_messages = [message.content for message in messages if isinstance(message,AIMessage)]

    if not ai_messages:
        raise ValueError("No AI response was generated")

    return ai_messages[-1]