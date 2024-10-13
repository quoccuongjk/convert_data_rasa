import pandas as pd
import yaml
import os
from train_intent import get_intents_from_file  

# Đọc intents từ file CSV
intents = get_intents_from_file('datachat.csv')

# Loại bỏ khoảng trắng ở hai đầu cho từng intent
intents = [intent.strip() for intent in intents]

if intents is None or len(intents) == 0:
    raise ValueError("Không có intents nào được tìm thấy trong file CSV.")

# Đọc dữ liệu từ file CSV
df = pd.read_csv('datachat.csv')

if df.empty:
    raise ValueError("DataFrame df không có dữ liệu. Vui lòng kiểm tra file CSV.")

# Danh sách các tệp YAML tương ứng với các intent
intent_files = {
    'booking': 'data/booking.yml',
    'doctor': 'data/doctor.yml',
    'clinic': 'data/clinic.yml',
    'hospital': 'data/hospital.yml',
    'symptom': 'data/symptom.yml',
    'consultant': 'data/consultant.yml',
    'patient': 'data/patient.yml',
    'health': 'data/health.yml'
}

# Hàm để đọc ví dụ từ tệp YAML
def read_examples_from_file(file_path):
    examples = set()
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            if data and 'nlu' in data:
                for item in data['nlu']:
                    examples.update(item['examples'].splitlines())
    return examples

# Thêm dữ liệu mới vào các tệp YAML
for index, row in df.iterrows():
    intent = intents[index]
    user_example = row['user'].strip()

    # Kiểm tra tệp tương ứng với intent
    if intent in intent_files:
        file_path = intent_files[intent]
        existing_examples = read_examples_from_file(file_path)

        # Kiểm tra xem ví dụ đã tồn tại chưa
        if user_example not in {example.lstrip('- ').strip() for example in existing_examples}:
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write(f"    - {user_example}\n")

# Ghi file domain.yml
responses = {}
for index, row in df.iterrows():
    intent = intents[index] 
    bot_response = row['bot']
    
    if f'utter_{intent}' not in responses:
        responses[f'utter_{intent}'] = [] 
    if {'text': bot_response} not in responses[f'utter_{intent}']:  
        responses[f'utter_{intent}'].append({'text': bot_response})  

# Đọc nội dung hiện tại của domain.yml
domain_data = {
    'intents': [],
    'responses': {}
}

if os.path.exists('domain.yml'):
    with open('domain.yml', 'r', encoding='utf-8') as domain_file:
        domain_data = yaml.safe_load(domain_file) or {}

# Thêm intents mới vào domain_data mà không bị trùng lặp
existing_intents = set(domain_data.get('intents', []))
for intent in intents:
    existing_intents.add(intent)

domain_data['intents'] = list(existing_intents)

# Thêm responses mới vào domain_data mà không bị trùng lặp
for intent, response_list in responses.items():
    if intent not in domain_data.get('responses', {}):
        domain_data.setdefault('responses', {})[intent] = []
        
    for response in response_list:
        if response not in domain_data['responses'][intent]:
            domain_data['responses'][intent].append(response)

# Ghi lại vào file domain.yml
with open('domain.yml', 'w', encoding='utf-8') as domain_file:
    # Ghi phiên bản
    domain_file.write("version: \"3.1\"\n\n")

    # Ghi intents
    domain_file.write("intents:\n")
    for intent in domain_data['intents']:
        domain_file.write(f"  - {intent}\n")
    
    # Ghi responses
    domain_file.write("\nresponses:\n")
    for intent, response_list in domain_data['responses'].items():
        domain_file.write(f"  {intent}:\n")
        for response in response_list:
            domain_file.write(f"  - text: \"{response['text']}\"\n")  # Sửa tại đây

# Ghi file stories.yml
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

# Ghi file stories.yml
with open('data/stories.yml', 'w', encoding='utf-8') as stories_file:
    yaml.dump({'stories': stories_data}, stories_file, allow_unicode=True, sort_keys=False)

print("Tệp domain.yml và stories.yml đã được tạo thành công.")