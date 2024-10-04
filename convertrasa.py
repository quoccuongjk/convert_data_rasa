import pandas as pd
import yaml
from train_intent import get_intents_from_file  

intents = get_intents_from_file('datachat.csv')
df = pd.read_csv('datachat.csv')

nlu_data = {}
for index, row in df.iterrows():
    intent = intents[index]
    user_example = row['user']
    
    if intent not in nlu_data:
        nlu_data[intent] = []
    if user_example not in nlu_data[intent]:
        nlu_data[intent].append(user_example)

nlu_data_formatted = []
for intent, examples in nlu_data.items():
    formatted_examples = [example.strip() for example in examples]
    nlu_data_formatted.append({
        'intent': intent,
        'examples': formatted_examples
    })

# Ghi file nlu.yml
with open('data/nlu.yml', 'w', encoding='utf-8') as nlu_file:
    nlu_file.write("nlu:\n")
    for item in nlu_data_formatted:
        nlu_file.write(f"  - intent: {item['intent']}\n")
        nlu_file.write("    examples: |\n")
        for example in item['examples']:
            nlu_file.write(f"      - {example}\n")  

responses = {}
for index, row in df.iterrows():
    intent = intents[index] 
    bot_response = row['bot']
    
    if f'utter_{intent}' not in responses:
        responses[f'utter_{intent}'] = [] 
    if {'text': bot_response} not in responses[f'utter_{intent}']:  
        responses[f'utter_{intent}'].append({'text': bot_response})  

stories_data = []
story_steps = {} 

for index, row in df.iterrows():
    intent = intents[index]  
    action = f'utter_{intent}'
    
    story_key = (intent, action)  

    if story_key not in story_steps:
        stories_data.append({
            'story': f'story_{intent}', 
            'steps': [
                {'intent': intent},
                {'action': action}
            ]
        })
        story_steps[story_key] = True 

# Cấu trúc domain_data
with open('domain.yml', 'w', encoding='utf-8') as domain_file:
    domain_file.write("intents:\n")
    for intent in intents:
        domain_file.write(f"  - {intent}\n")
    
    domain_file.write("responses:\n")
    for intent, response_list in responses.items():
        domain_file.write(f"  {intent}:\n")
        for response in response_list:
            domain_file.write(f"  - text: {response['text']}\n")
# Ghi file stories.yml
with open('data/stories.yml', 'w', encoding='utf-8') as stories_file:
    yaml.dump({'stories': stories_data}, stories_file, allow_unicode=True, sort_keys=False)