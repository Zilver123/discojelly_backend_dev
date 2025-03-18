# Assuming services.json is in the same directory
import json

def service_builder(name, category, user_name, model, instruction, tools):
    new_service = {
        'name': name,
        'category': category,
        'user_name': user_name,
        'config': {
            'model': model,
            'instruction': instruction,
            'tools': tools
        }
    }

    # Read the existing JSON data
    with open('services.json', 'r+') as file:
        existing_data = json.load(file)

    # Add the new service to the services list
    if 'services' in existing_data:
        existing_data['services'].append(new_service)
    else:
        existing_data['services'] = [new_service]

    # Write the updated JSON data back to the file
    with open('services.json', 'w') as file:
        json.dump(existing_data, file, indent=4)

    return "Service successfully created"