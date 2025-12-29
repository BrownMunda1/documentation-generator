from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

from llm_utility.caller import call_llm
from llm_utility.prompts import (
    CHUNK_SUMMARY_PROMPT,
    DIRECTORY_SUMMARY_PROMPT,
    FILE_SUMMARY_PROMPT,
    PROJECT_SUMMARY_PROMPT,
)


# Chunk summarizer
def chunk_summarizer(chunk: Document):

    chunk_code = str(chunk.page_content)

    chunk_summarizer_prompt = PromptTemplate(
        template=CHUNK_SUMMARY_PROMPT, input_variables=["code_chunk_content"]
    ).format(code_chunk_content=chunk_code)

    return call_llm(prompt=chunk_summarizer_prompt)


def file_summarizer(file_chunk_summaries: list):

    file_summarizer_prompt = PromptTemplate(
        template=FILE_SUMMARY_PROMPT, input_variables=["file_summaries"]
    ).format(file_summaries=file_chunk_summaries)

    return call_llm(prompt=file_summarizer_prompt)


def directory_summarizer(directory_summaries: list):
    directory_summarizer_prompt = PromptTemplate(
        template=DIRECTORY_SUMMARY_PROMPT, input_variables=["directory_summaries"]
    ).format(directory_summaries=directory_summaries)

    return call_llm(prompt=directory_summarizer_prompt)


def project_summarizer(summaries: list):
    summarizer_prompt = PromptTemplate(
        template=PROJECT_SUMMARY_PROMPT, input_variables=["summaries"]
    ).format(summaries=summaries)

    return call_llm(prompt=summarizer_prompt)
