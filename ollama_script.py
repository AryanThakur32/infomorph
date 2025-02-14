import ollama 

# response = ollama.chat(
#     model='llama3.1',
#      messages=[
#   {
#     'role': 'user',
#     'content': 'Why is the sky blue?',
#   },
# ])
# print(response['message']['content'])

response =ollama.generate(model='llama3.1',prompt='why is the sky blue?')
print(response['response'])