from loguru import logger
from pydantic import HttpUrl

from github_handler import repo_cloner

# from knowledge_graph.create_kg import create_kg
from knowledge_graph.prepare_data import create_code_data

logger.info("Starting up now...")

project_dir = repo_cloner.clone_repo(
    repo_url=HttpUrl(url="https://github.com/BrownMunda1/cicd-automation.git"),
    branch="main",
    should_clone=False,
)

result = create_code_data(project_dir=project_dir)

# print(result)

# response = create_kg(project_dir=project_dir)
# print(response.content)

# docs = create_docs(project_dir=project_dir)

# summaries: dict[str, list] = {}

# for doc in docs:
#     summary = chunk_summarizer(doc)
#     file = str(Path(doc.metadata["source"].split(str(project_dir))[1]).as_posix())[1:]
#     if not summaries.get(file, None):
#         summaries[file] = []
#     summaries[file].append(summary.content)


# ## Combine per file -> then combine per directory -> then whole project

# while True:

#     if not any(len(s.split("/")) > 1 for s in list(summaries.keys())):
#         break

#     new_summaries: dict[str, list] = {}
#     for i, j in summaries.items():

#         if i.endswith(".py"):
#             # File Summaries
#             temp = i.split("/")
#             dir_path = "/".join(temp[:-1])
#             summary = file_summarizer(file_chunk_summaries=j)
#             if not new_summaries.get(dir_path, None):
#                 new_summaries[dir_path] = []
#             new_summaries[dir_path].append(summary.content)
#         else:
#             # Directory summaries
#             temp = i.split("/")
#             dir_path = "/".join(temp[:-1])
#             summary = directory_summarizer(directory_summaries=j)
#             if not new_summaries.get(dir_path, None):
#                 new_summaries[dir_path] = []
#             new_summaries[dir_path].append(summary.content)

#     summaries = new_summaries

# final_summary = project_summarizer(summaries=summaries)

# print(final_summary.content)

logger.info("That's it")
