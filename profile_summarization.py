import yaml
import difflib


def find_nearest_key(yaml_data, target_key):
    keys = yaml_data.keys()
    closest_match = difflib.get_close_matches(target_key, keys, n=1)
    return closest_match[0] if closest_match else None


def generate_profile_summarization_prompt(requirement):
    try:
        with open('profile_summarization.yaml', 'r') as file:
            data = yaml.safe_load(file)

        if requirement in data['prompts']:
            prompt = data['prompts'][requirement]
        else:
            _requirement = find_nearest_key(data, requirement)
            if _requirement is not None:
                prompt = data['prompts'][_requirement]
            else:
                prompt = data['prompts']['default']

        return prompt
    except FileNotFoundError:
        print("YAML file missing in local directory.....")
        return None
