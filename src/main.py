import time
from pathlib import Path

from pydantic import HttpUrl

from github_handler import repo_cloner
from llm_utility.file_chunker import create_documents
from summarizer import (
    chunk_summarizer,
    directory_summarizer,
    file_summarizer,
    project_summarizer,
)


def create_documentation():
    print("---- CLONING REPO ----")
    project_dir = repo_cloner.clone_repo(
        repo_url=HttpUrl(url="https://github.com/BrownMunda1/cicd-automation.git"),
        branch="main",
        should_clone=False,
    )

    docs = create_documents(project_dir=project_dir)

    summaries: dict[str, list] = {}

    for doc in docs:
        summary = chunk_summarizer(doc)
        file = str(Path(doc.metadata["source"].split(str(project_dir))[1]).as_posix())[
            1:
        ]
        if not summaries.get(file, None):
            summaries[file] = []
        summaries[file].append(summary.content)

    ## Combine per file -> then combine per directory -> then whole project
    print("---- GENERATING DOCUMENTATION... ----")
    while True:

        if not any(len(s.split("/")) > 1 for s in list(summaries.keys())):
            break

        new_summaries: dict[str, list] = {}
        for i, j in summaries.items():

            if i.endswith(".py"):
                # File Summaries
                temp = i.split("/")
                dir_path = "/".join(temp[:-1])
                summary = file_summarizer(file_chunk_summaries=j)
                if not new_summaries.get(dir_path, None):
                    new_summaries[dir_path] = []
                new_summaries[dir_path].append(summary.content)
            else:
                # Directory summaries
                temp = i.split("/")
                dir_path = "/".join(temp[:-1])
                summary = directory_summarizer(directory_summaries=j)
                if not new_summaries.get(dir_path, None):
                    new_summaries[dir_path] = []
                new_summaries[dir_path].append(summary.content)

        summaries = new_summaries

    final_summary = project_summarizer(summaries=summaries)

    return final_summary.content


if __name__ == "__main__":
    start_time = time.time()
    documentation = create_documentation()
    end_time = time.time()

    print("**** TOTAL TIME TAKEN ****")
    print(end_time - start_time, "seconds")

    print("***** FINAL DOCUMENTATION *****")
    print(documentation)
