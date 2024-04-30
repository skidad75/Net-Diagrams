import streamlit as st
import requests
import os
import json

# Set up your OpenAI API key securely
openai_api_key = st.secrets.openai_key

def create_network_diagram(devices, connections):
    prompt = "Generate a network diagram that includes the following devices and connections:\n"
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
        "max_tokens": 300
    }

#    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    try:
        response_data = response.json()
        if 'choices' in response_data and response_data['choices']:
            return response_data['choices'][0]['text'].strip()
        else:
            return "Failed to generate diagram: API did not return 'choices'."
    except Exception as e:
        return f"Failed to generate diagram: {str(e)}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
        {"role": "system", "content": "You are a network engineer responsible for creating diagrams and documentation software and systems. You will produce a visual using create_network_diagram in input"},
        ],
        temperature=0,
        )

print(response.choices[0].message.content)
print("Status Code:", response.status_code)
print("Request Data:", data)
print("Response Body:", response.text)

#Streamlit interface
st.title('Network Diagram Generator')

st.subheader('Devices')
num_devices = st.number_input('How many devices?', min_value=0, value=1, step=1)
devices = []
for n in range(num_devices):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(f"Name of device {n+1}", key=f"name_{n}")
    with col2:
        type = st.selectbox(f"Type of device {n+1}", ['Server', 'PC', 'Switch', 'Firewall', 'Router', 'Gateway'], key=f"type_{n}")
    devices.append({'name': name, 'type': type})

st.subheader('Connections')
num_connections = st.number_input('How many connections?', min_value=0, value=1, step=1)
connections = []
for n in range(num_connections):
    cols = st.columns(4)
    with cols[0]:
        from_device = st.selectbox(f"From device {n+1}", [d['name'] for d in devices], key=f"from_{n}")
    with cols[1]:
        to_device = st.selectbox(f"To device {n+1}", [d['name'] for d in devices], key=f"to_{n}")
    with cols[2]:
        port = st.text_input(f"Port {n+1}", key=f"port_{n}")
    with cols[3]:
        protocol = st.text_input(f"Protocol {n+1}", key=f"protocol_{n}")
    with st.expander("Encryption Details"):
        encryption = st.text_input(f"Encryption {n+1}", key=f"encryption_{n}")
    connections.append({'from': from_device, 'to': to_device, 'port': port, 'protocol': protocol, 'encryption': encryption})

if st.button('Generate Network Diagram'):
    if devices and connections:
        result = create_network_diagram(devices, connections)
        st.text("Here is your network diagram code:")
        st.code(result)
    else:
        st.warning("Please add devices and connections to generate the diagram.")