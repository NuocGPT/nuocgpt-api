"""
Load langchain configs contains LLMChain model and Prompt.
- LLMChain: https://python.langchain.com/docs/modules/model_io/models/llms/llm_serialization
- Prompt: https://python.langchain.com/docs/modules/model_io/prompts/prompt_templates/prompt_serialization
"""
import os.path
import yaml
from langchain import BasePromptTemplate, PromptTemplate
from langchain.prompts import load_prompt

from ai.core.constants import BaseConstants

class LangChainDataLoader:
    """Langchain Data loader."""
    config: dict[str, dict[str, str]]
    prompts: dict[str, BasePromptTemplate]
    
    def __init__(self):
        self.prompts = {}

        with open(os.path.join(BaseConstants.ROOT_PATH, "configs/prompts/config.yaml"), "r") as f:
            self.config = yaml.safe_load(f)

        self._load_prompt()

    def _load_prompt(self):
        """Load prompt."""
        for title, info in self.config.items():
            self.prompts[title] = load_prompt(os.path.join(BaseConstants.ROOT_PATH, info["filepath"]))

    def preprocessing_qa_prompt(
        self,
        language: str,
        metadata: str,
        chat_history = None,
        relevant_answer: str = None,
    ):
        for prompt_title in ["qaPrompt", "qaWithoutDocsPrompt"]:
            qa_template = self.prompts[prompt_title].template
            qa_template += (
                        f"Based on the conversation chat history and the new question of customer, "
                        f"write a helpful response in {language} language"
                    )
            
            if relevant_answer:
                qa_template += (
                    f"Here is a potential relevant answer. You should use information from it to generate the response."
                    f"Relevant answer: {relevant_answer}"
                )

            qa_template += "\nResponse:\n\n"

            if prompt_title == "qaPrompt":
                qa_template = qa_template.format(
                                    metadata=metadata,
                                    context="{context}",
                                    question="{question}",
                                )
                self.prompts[prompt_title] = PromptTemplate(template=qa_template, input_variables=["context", "question"])
            else:
                qa_template = qa_template.format(
                                    chat_history = chat_history,
                                    question="{question}",
                                )
                self.prompts[prompt_title] = PromptTemplate(template=qa_template, input_variables=["question"])
