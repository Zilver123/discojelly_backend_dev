# Imports
from openai import OpenAI
import json
import os

KEY = os.getenv('OPENAI_API_KEY')
if KEY is None:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

class Service:
    def __init__(self, api_key, config):
        self.client = OpenAI(api_key=api_key)
        self.tools = config[0]["function"]["parameters"]["properties"]["tools"]
        self.model = config[0]["function"]["parameters"]["properties"]["model"]
        self.context = [{"role": "system", "content": config[0]["function"]["parameters"]["properties"]["instructions"]}]
    
    def call_function(self, name, args):
        if name == "get_weather":
            return "The weather is 32 degrees"

    def call_model(self, message):
        if message is not None:
            self.context.append({"role": "user", "content": message})
        print(self.context)
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.context,
            tools=self.tools,
        )
        return completion

    def main(self, message):
        completion = self.call_model(message)

        if completion.choices[0].message.tool_calls is not None:
            for tool_call in completion.choices[0].message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                result = self.call_function(name, args)
                self.context.append(completion.choices[0].message)
                self.context.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
            return self.main(None)
        else:
            self.context.append(completion.choices[0].message)
            return completion.choices[0].message.content


tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current temperature for provided coordinates in celsius.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"}
            },
            "required": ["latitude", "longitude"],
            "additionalProperties": False
        },
        "strict": True
    },
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current temperature for provided coordinates in celsius.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"}
            },
            "required": ["latitude", "longitude"],
            "additionalProperties": False
        },
        "strict": True
    },
}]

config = [{
    "type": "function",
    "function": {
        "name": "plan_marketing",
        "description": "Get a step by step marketing plan",
        "parameters": {
            "type": "object",
            "properties": {
                "model": "gpt-4o",
                "message": {"type": "string"},
                "instructions": "You are a weather guru",
                "tools": tools,

            },
            "required": ["message"],
            "additionalProperties": False
        },
        "strict": True
    }
}]


agent = Service(api_key=KEY, config=config)


while True:
    try:
        message = input("Enter your message (or type 'exit' to quit): ")
        if message.lower() in ['exit', 'quit']:
            print("Exiting...")
            break
        print(agent.main(message))
    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print(f"An error occurred: {e}")