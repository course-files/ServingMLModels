import requests

# Go to: https://publicapis.io/apis
# Go to: https://api.stackexchange.com/docs

response = requests.get('https://api.stackexchange.com/2.3/questions?order=desc&sort=activity&site=stackoverflow')
# print(response.json())

# print(response.json()['items'])

for data in response.json()['items']:
    print(data['title'])
    print(data['link'])
    print(data['answer_count'])
    print()
