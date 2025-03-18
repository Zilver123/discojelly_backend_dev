# Imports
from openai import OpenAI
import json
from config.py import KEY

"""
client = OpenAI(api_key=KEY)


# Function call
def call_service(input):
    return "The weather is 32 degrees"

def call_model(messages, services):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=services,
    )
    return completion

# Tool list 

services = [{
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
    }
},
{
    "type": "function",
    "function": {
        "name": "plan_marketing",
        "description": "Get a step by step marketing plan",
        "parameters": {
            "type": "object",
            "properties": {
                "model": "yes",
                "message": {"type": "string"},
                "instructions": "You are a marketing planner",
                "tools": "none",

            },
            "required": ["message"],
            "additionalProperties": False
        },
        "strict": True
    }
}]

# Model call

def main(services, messages):
    completion = call_model(messages, services)

    if completion.choices[0].message.tool_calls is not None:
        tool_call = completion.choices[0].message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        result = call_service(args)
        messages.append(completion.choices[0].message)  # append model's function call message
        messages.append({                               # append result message
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result)
        })
        return main([], messages)
    else:
        return completion.choices[0].message.content

messages = [{"role": "user", "content": "What's the weather like in Paris today?"}]
print(main(services, messages))

"""



class Service:
    def __init__(self, api_key, config):
        self.client = OpenAI(api_key=api_key)
        self.tools = config[0]["function"]["parameters"]["properties"]["tools"]
        self.model = config[0]["function"]["parameters"]["properties"]["model"]
        self.context = [{"role": "system", "content": config[0]["function"]["parameters"]["properties"]["instructions"]}]

    def call_service(self, input):
        return "The weather is 32 degrees"

    def call_model(self, messages, tools):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
        )
        return completion

    def main(self, messages, tools):
        completion = self.call_model(messages, tools)

        if completion.choices[0].message.tool_calls is not None:
            tool_call = completion.choices[0].message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            result = self.call_service(args)
            messages.append(completion.choices[0].message)  # append model's function call message
            messages.append({                               # append result message
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
            return self.main(messages, [])
        else:
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
    }
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
                "instructions": "You are a marketing planner",
                "tools": tools,

            },
            "required": ["message"],
            "additionalProperties": False
        },
        "strict": True
    }
}]


agent = Service(api_key=KEY, config=config)


messages = [{"role": "user", "content": "What's the weather like in Paris today?"}]
print(agent.main(messages, tools))