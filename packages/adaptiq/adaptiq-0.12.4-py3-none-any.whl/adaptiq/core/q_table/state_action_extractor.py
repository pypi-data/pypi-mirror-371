import json
import re
from typing import Dict, Tuple

from langchain_core.prompts import PromptTemplate

from adaptiq.core.abstract.q_table.base_state_action_extractor import (
    BaseStateActionExtractor,
)
from adaptiq.core.entities import LogItem, LogState, ProcessedLogs
from adaptiq.core.entities.adaptiq_parsers import StateActionMapping


class StateActionExtractor(BaseStateActionExtractor):
    """
    Class for extracting state and action information from execution data and
    transforming it into a standardized format.
    """

    def _create_prompt_template(self) -> PromptTemplate:
        """Create the prompt template for state-action extraction."""
        return PromptTemplate(
            input_variables=["input_data"],
            template="""
            You are an AI assistant helping to extract and transform state and action information.

            Given the following execution data:
            {input_data}

            Extract and transform the information into a state-action mapping, using the following rules:

            - From the "state" field:
                - Extract the **core meaning** of "current_sub_task_or_thought" → this becomes the first element of the state tuple
                - Use "last_action_taken" → second element of the state tuple
                - Use "last_outcome" → third element of the state tuple
                - Extract the **main role or situation** from "agent_context" → fourth element of the state tuple

            - From "agent_action":
                - Extract only the tool name (keep it concise, e.g. "FileReadTool")

            Format the output as a valid JSON object **exactly** like this:
            {{ "state": ["InformationRetrieval_Company", "None", "None", "company background"], "action": "FileReadTool" }}

            Rules:
            - Focus on capturing the **important ideas** in each tuple element; summarize clearly and concisely (2–3 words max per element)
            - Use 'None' if no relevant info exists
            - The action must be a **clean tool name only**, no extra description
            - Output must be valid JSON that can be parsed by Python's json.loads()
            - Return ONLY the JSON object, nothing else.
            """,
        )

    def _extract_raw_state_and_action(self, log_data: LogItem) -> Tuple[LogState, str]:
        """
        Extract raw state and action from the input data.

        Args:
            log_data (dict): The input data containing state and action information.

        Returns:
            Tuple[LogState, str]: A tuple containing the extracted state as a LogState object and the action as a string.
        """
        try:

            # Extract state and action from the input data
            state_dict = log_data.key.state
            action_str = log_data.key.agent_action

            return state_dict, action_str

        except Exception as e:
            raise ValueError(f"Failed to extract state and action: {str(e)}")

    def _transform_with_llm(
        self, state_dict: LogState, action_str: str
    ) -> StateActionMapping:
        """
        Use LangChain and OpenAI to transform the extracted state and action.

        Args:
            state_dict (dict): The extracted state dictionary.
            action_str (str): The extracted action string.

        Returns:
            StateActionMapping: The transformed state-action mapping.
        """
        input_for_llm = {"state": state_dict.model_dump(), "action": action_str}

        chain = self.prompt_template | self.llm
        result = chain.invoke({"input_data": json.dumps(input_for_llm)})

        # Extract the JSON from the result
        try:
            # Try to find JSON in the content
            content = result.content
            json_match = re.search(r"({.*})", content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                return StateActionMapping(**json.loads(json_str))
            else:
                return StateActionMapping(**json.loads(content))
        except Exception as e:
            raise ValueError(f"Failed to parse LLM response: {str(e)}")
