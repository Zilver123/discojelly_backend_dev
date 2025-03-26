# Imports
from openai import OpenAI
import json
import os
import tool_replicate
from tools_config import tools

KEY = os.getenv('OPENAI_API_KEY')
if KEY is None:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

class Service:
    def __init__(self, api_key, config):
        self.client = OpenAI(api_key=api_key)
        self.tools = config["tools"]
        self.model = config["model"]
        self.context = [{"role": "system", "content": config["instructions"]}]
    
    def run_tool(self, name, args):
        if name == "generate_image":
            return tool_replicate.generate("black-forest-labs/flux-1.1-pro", args)
        elif name == "generate_music_v2":
            return tool_replicate.generate("meta/musicgen:671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedcfb", args)
        elif name == "generate_music":
            return tool_replicate.generate("minimax/music-01", args)

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

    def call_tools(self, payload):
        for tool_call in payload.message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            result = self.run_tool(name, args)
            self.context.append(payload.message)
            self.context.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(result)})

    def main(self, message):
        completion = self.call_model(message)
        payload = completion.choices[0]

        if payload.message.tool_calls is not None:
            self.call_tools(payload)
            return self.main(None)
        else:
            self.context.append(payload.message)
            return payload.message.content

config = {
    "model": "gpt-4",
    "instructions": "You are a creator tool for content creators. You can generate images, videos, and text.",
    "tools": tools
}

if __name__ == "__main__":
    print("Initializing service...")
    agent = Service(api_key=KEY, config=config)
    print("Service initialized successfully!")

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