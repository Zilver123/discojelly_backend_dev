# Imports
from openai import OpenAI
import json
import os
import tool_replicate

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

tools = [{
    "type": "function",
    "function": {
        "name": "generate_image",
        "description": "Generate an image based on text prompt and optional parameters.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Text prompt for image generation"
                },
                "seed": {
                    "type": "integer",
                    "description": "Random seed. Set for reproducible generation"
                },
                "width": {
                    "type": "integer",
                    "description": "Width of the generated image in text-to-image mode. Must be between 256 and 1440, multiple of 32."
                },
                "height": {
                    "type": "integer",
                    "description": "Height of the generated image in text-to-image mode. Must be between 256 and 1440, multiple of 32."
                },
                "aspect_ratio": {
                    "type": "string",
                    "description": "Aspect ratio for the generated image",
                    "enum": ["custom", "1:1", "16:9", "3:2", "2:3", "4:5", "5:4", "9:16", "3:4", "4:3"]
                },
                "image_prompt": {
                    "type": "string",
                    "description": "Image to use with Flux Redux. Must be jpeg, png, gif, or webp."
                },
                "output_format": {
                    "type": "string",
                    "description": "Format of the output images.",
                    "enum": ["webp", "jpg", "png"]
                },
                "output_quality": {
                    "type": "integer",
                    "description": "Quality when saving the output images, from 0 to 100."
                },
                "safety_tolerance": {
                    "type": "integer",
                    "description": "Safety tolerance, 1 is most strict and 6 is most permissive"
                },
                "prompt_upsampling": {
                    "type": "boolean",
                    "description": "Automatically modify the prompt for more creative generation"
                }
            },
            "required": ["prompt", "seed", "width", "height", "aspect_ratio", "image_prompt", "output_format", "output_quality", "safety_tolerance", "prompt_upsampling"],
            "additionalProperties": False
        },
        "strict": True
    }
}]

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