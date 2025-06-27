import sys
import logging
from llama_index.core.agent import ReActAgent
from agents.models import get_base_agent_model

#Logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

class OrchestratorAgent:
    def __init__(self):
        self.tools = []
        self.llm = get_base_agent_model()
        self.agent = ReActAgent.from_tools(llm=self.llm, tools=self.tools, context=self.system_prompt, verbose=True)

    async def __call__(self, question: str) -> str:
        response_object = self.agent.chat(question)
        full_response_text = str(response_object)
        
        return full_response_text
