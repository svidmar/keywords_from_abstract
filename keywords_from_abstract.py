# This script can be used to fetch an abstract from research output in Pure, send it to ChatGTP, generate keywords, and write these keywords back into Pure.

import requests
import os

# Fetch the abstract from the Pure API
input_api_url = "https://vbn.aau.dk/ws/api/research-outputs/79678cf3-dc6b-4387-b563-8f5c26facb9f"
api_key = os.environ.get('PURE_API_KEY', '')
headers = {"api-key": api_key}

response = requests.get(input_api_url, headers=headers)
if response.status_code != 200:
    print("Error fetching data from the API:", response.text)
    exit()

data = response.json()
abstract = data.get("abstract", "Abstract not found")

# Use ChatGPT to generate keywords based on the abstract from Pure
chatgpt_api_key = os.environ.get('CHATGPT_API_KEY', '')
chatgpt_api_url = "https://api.openai.com/v1/chat/completions"
messages = [{"role": "user", "content": f"Generate five keywords based on the following abstract: {abstract}"}]
data = {"model": "gpt-3.5-turbo", "messages": messages, "max_tokens": 30}
headers = {"Authorization": f"Bearer {chatgpt_api_key}", "Content-Type": "application/json"}

response = requests.post(chatgpt_api_url, json=data, headers=headers)
if response.status_code != 200:
    print("Error processing data with ChatGPT:", response.text)
    exit()

chatgpt_output = response.json()["choices"][0]["message"]["content"].strip()
print("Generated Keywords:", chatgpt_output)

# Remove numbering from keywords
keywords = [keyword.strip().lstrip("1234567890. ") for keyword in chatgpt_output.split('\n')]

# Build the JSON structure with individual keywords
formatted_keywords = [
    {
        "pureId": 549595282,
        "locale": "en_GB",
        "freeKeywords": keywords
    }
]

# Use the same environment variable for api_key
api_key = os.environ.get('PURE_API_KEY', '')

json_data = {
    "keywordGroups": [
        {
            "typeDiscriminator": "FreeKeywordsKeywordGroup",
            "pureId": 549595280,
            "logicalName": "keywordContainers",
            "name": {"en_GB": "Keywords", "da_DK": "Emneord"},
            "keywords": formatted_keywords
        }
    ]
}

update_api_url = "https://vbn.aau.dk/ws/api/research-outputs/79678cf3-dc6b-4387-b563-8f5c26facb9f"
headers = {"accept": "application/json", "api-key": api_key, "Content-Type": "application/json"}

response = requests.put(update_api_url, json=json_data, headers=headers)
if response.status_code == 200:
    print("Keywords updated successfully!")
else:
    print("Error updating keywords:", response.text)
