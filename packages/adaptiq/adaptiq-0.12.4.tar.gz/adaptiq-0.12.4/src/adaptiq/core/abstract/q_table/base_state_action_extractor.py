from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import PromptTemplate

from adaptiq.core.entities import LogItem, LogState, ProcessedLogs, StateActionMapping


class BaseStateActionExtractor(ABC):
    """
    Abstract base class for extracting state and action information from execution data
    and transforming it into a standardized format.
    """

    def __init__(self, llm: BaseChatModel):
        """
        Initialize the extractor.

        Args:
            llm (BaseChatModel): The language model used for transformation.
        """
        self.llm = llm
        self.prompt_template = self._create_prompt_template()

    @abstractmethod
    def _create_prompt_template(self) -> PromptTemplate:
        """
        Create the prompt template for state-action extraction.

        Returns:
            PromptTemplate instance
        """
        pass

    @abstractmethod
    def _extract_raw_state_and_action(self, log_data: LogItem) -> Tuple[Dict, str]:
        """
        Extract raw state and action from the input data.

        Args:
            input_data: The input data containing state and action information

        Returns:
            tuple: (state_dict, action_str)
        """
        pass

    @abstractmethod
    def _transform_with_llm(
        self, state_dict: LogState, action_str: str
    ) -> StateActionMapping:
        """
        Use LLM to transform the extracted state and action.

        Args:
            state_dict: The extracted state dictionary
            action_str: The extracted action string

        Returns:
            StateActionMapping: The transformed state and action mapping
        """
        pass

    def extract(self, input_data: LogItem) -> StateActionMapping:
        """
        Extract and transform state and action from the input data.

        Args:
            input_data: The input data containing state and action information

        Returns:
            StateActionMapping: The transformed state and action mapping
        """
        state_dict, action_str = self._extract_raw_state_and_action(input_data)
        transformed_data = self._transform_with_llm(state_dict, action_str)
        return transformed_data

    def process_batch(self, parsed_logs: ProcessedLogs) -> List[StateActionMapping]:
        """
        Process a batch of input data.

        Args:
            parsed_logs: ProcessedLogs containing a list of log items

        Returns:
            List[StateActionMapping]: List of transformed state-action mappings
        """
        results: List[StateActionMapping] = []
        for log_data in parsed_logs.processed_logs:
            try:
                result = self.extract(log_data)
                results.append(result)
            except Exception as e:
                print(f"Error processing input: {str(e)}")
                results.append({"error": str(e)})
        return results
