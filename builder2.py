import service_builder
from openai import OpenAI
import json
import os

KEY = os.getenv('OPENAI_API_KEY')
if KEY is None:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")


client = OpenAI(api_key=KEY)
tools = [{
    "type": "function",
    "function": {
        "name": "create_service",
        "description": "Create a service with the following parameters.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "category": {"type": "string"},
                "user_name": {"type": "string"},
                "model": {"type": "string"},
                "instruction": {"type": "string"},
                "tools": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["name", "category", "user_name", "model", "instruction", "tools"],
            "additionalProperties": False
        },
        "strict": True
    }
}]

messages = [{"role": "user", "content": "Build a service with the following parameters: Name: TESTTTT Category: DataProcessing User Name: JohnDoe Model: gpt-4o Instruction: This service processes data and provides insights. Tools: APITool, WebhookTool"}]
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
)


tool_call = completion.choices[0].message.tool_calls[0]
args = json.loads(tool_call.function.arguments)

result = service_builder.service_builder(args["name"], args["category"], args["user_name"], args["model"], args["instruction"], args["tools"])
messages.append(completion.choices[0].message)  # append model's function call message
messages.append({                               # append result message
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": str(result)
})

completion_2 = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
)

print(completion_2.choices[0].message.content)