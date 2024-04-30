import streamlit as st
import requests
import os
import json

# Set up your OpenAI API key securely
openai_api_key = st.secrets.openai_key


def create_network_diagram(devices, connections):
    # Building a detailed prompt
    prompt = "Generate a network diagram code that includes the following devices and connections:\n"
    for device in devices:
        prompt += f"- {device['type']} named {device['name']}\n"
    prompt += "Connections:\n"
    for conn in connections:
        prompt += f"- {conn['from']} to {conn['to']} using port {conn['port']} over {conn['protocol']} with {conn['encryption']} encryption\n"
    prompt += "The diagram should reflect network engineering standards."

    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "prompt": prompt,
        "max_tokens": 250
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    print("Status Code:", response.status_code)  # Print the status code
    print("Response Body:", response.text)  # Print the full response body

    try:
        response_data = response.json()
        if 'choices' in response_data and response_data['choices']:
            return response_data['choices'][0]['text'].strip()
        else:
            return "Failed to generate diagram: API did not return 'choices'."
    except Exception as e:
        return f"Failed to generate diagram: {str(e)}"