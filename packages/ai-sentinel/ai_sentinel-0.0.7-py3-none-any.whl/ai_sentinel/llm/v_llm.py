"""
from openai import OpenAI
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="token-abc123",
)

completion = client.chat.completions.create(
  model="NousResearch/Meta-Llama-3-8B-Instruct",
  messages=[
    {"role": "user", "content": "Hello!"}
  ]
)

print(completion.choices[0].message)
"""

from typing import Optional, Any

from openai import OpenAI, AuthenticationError
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.parsed_chat_completion import ParsedChatCompletion

from ai_sentinel.llm.base import BaseLLMClient
from ai_sentinel.core.models import LLMResponse

class OpenSourceVLLM(BaseLLMClient):
    '''Open Source LLM client implementation using vLLM's server to create a OpenAI-Compatible Server'''

    def __init__(
            self, 
            model: str, 
            api_base: str,
            api_key: Optional[str] = 'EMPTY', # API key can be any string, as it's not validated by vLLM by default
            timeout: Optional[float] = 30.0, 
            **kwargs
        ):
        super().__init__(api_key, model, timeout, **kwargs)    

        if not api_base or not isinstance(api_base, str):
            raise ValueError('Base URL must be a non-empty string')

        self.api_base = api_base

        self.client = OpenAI( # call vllm server usin openai
            api_key=self.api_key,
            base_url=api_base,
            timeout=self.timeout
        )

    async def generate_text_async(
            self, 
            prompt: str, 
            system_prompt: Optional[str] = None, 
            context: Optional[list[dict[str,str]]] = None,
            temperature: Optional[float] = 0.0,
            **kwargs # supply response format in kwargs
        ) -> LLMResponse:
        
        if not prompt or not isinstance(prompt, str):
            raise ValueError('Prompt must be a non-empty string')
        
        response_format: Optional[Any] = kwargs.get('response_format')

        message: list = []
        response = None

        # check if there is a system prompt given
        if system_prompt:
            message.append({
                'role': 'system',
                'content': system_prompt
            })
        # check if there is context given
        if context:
            message.extend(context)

        message.append({
            'role': 'user',
            'content': prompt
        })

        if response_format:
            # use parse instead of create bc using structured output 
            response: ParsedChatCompletion = self.client.chat.completions.parse(
                model=self.model,
                messages=message,
                temperature=temperature,
                response_format=response_format
            )
        else:
            response: ChatCompletion = self.client.chat.completions.create(
                model=self.model,
                messages=message,
                temperature=temperature
            )
        formatted_response: LLMResponse = self._format_llm_response(response)
        return formatted_response
    
    def _format_llm_response(self, response: ChatCompletion | ParsedChatCompletion) -> LLMResponse:
        '''Convert response to built in Model type to a response type of LLMResponse'''

        output: LLMResponse = LLMResponse(
            content=response.choices[0].message.content,
            model = self.model
        )
        output.usage = {
            'model_tokens': response.usage.completion_tokens,
            'prompt_tokens': response.usage.prompt_tokens,
            'total_tokens': response.usage.total_tokens,
        }

        output.response_time_ms = output.timestamp.timestamp() - response.created
        output.finish_reason = response.choices[0].finish_reason
        return output

    async def validate_async(self) -> bool:
        # make a simple API call
        try:
            self.client.models.list()
            # if call is successful then the key is valid
            return True
        except Exception as e:
            print(f'An unexpected error occurred while connecting to the LLM server: {e}')
            return False