# # Use a pipeline as a high-level helper
# from transformers import pipeline
# import torch
# print(torch.__version__)
# pipe = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.2")

# prompt = "Generate a one-sentence description about Paris:"
# response = pipe(prompt, max_length=50, num_return_sequences=1)[0]['generated_text']
# print(response)