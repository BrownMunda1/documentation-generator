from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI

def call_llm(prompt: str, structured_output_class: Any = None, model: str = "gemini-2.5-flash"):

    llm = ChatGoogleGenerativeAI(model=model)

    if structured_output_class:
        response = llm.with_structured_output(structured_output_class).invoke(prompt)
    else:
        response = llm.invoke(prompt)

    return response
