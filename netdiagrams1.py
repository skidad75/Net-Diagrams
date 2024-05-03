import streamlit as st
import requests
import json
from openai import OpenAI
client = OpenAI

# Setting up headers for the API request
openai_api_key = st.secrets["openai_key"]  # Ensure your Streamlit secrets are correctly set
headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
        }

# Function to create a network diagram
def create_network_diagram(devices, connections):
    # Constructing the prompt for the network diagram
    prompt = "Generate a network diagram that includes the following devices and connections:\n"
    for device in devices:
        prompt += f"- {device['type']} named {device['name']}\n"
    prompt += "Connections:\n"
    for conn in connections:
        prompt += f"- {conn['from']} to {conn['to']} using port {conn['port']} over {conn['protocol']} with {conn['encryption']} encryption\n"
    prompt += "The diagram should reflect network engineering standards."

   
    # Sending the request to OpenAI API
    try:
        response_data = client.chat.completions.create(
            model="gpt3.5-turbo-0125",
            response_format={"type": "json_object" },
            messages=response.choices[0]
        if 'choices' in response_data and response_data['choices']:
            print(response.choices[0].message.content)
        else:
            return "Failed to generate diagram: API did not return 'choices'."
    except Exception as e:
        return f"Failed to generate diagram: {str(e)}"

# Streamlit user interface
st.title('Network Diagram Generator')
st.subheader('Devices')
num_devices = st.number_input('How many devices?', min_value=0, value=1, step=1)
devices = []
for n in range(num_devices):
    with st.container():
        name = st.text_input(f"Name of device {n+1}", key=f"name_{n}")
        type = st.selectbox(f"Type of device {n+1}", ['Server', 'PC', 'Switch', 'Firewall', 'Router', 'Gateway'], key=f"type_{n}")
    devices.append({'name': name, 'type': type})

st.subheader('Connections')
num_connections = st.number_input('How many connections?', min_value=0, value=1, step=1)
connections = []
for n in range(num_connections):
    with st.container():
        from_device = st.selectbox(f"From device {n+1}", [d['name'] for d in devices], key=f"from_{n}")
        to_device = st.selectbox(f"To device {n+1}", [d['name'] for d in devices], key=f"to_{n}")
        port = st.text_input(f"Port {n+1}", key=f"port_{n}")
        protocol = st.text_input(f"Protocol {n+1}", key=f"protocol_{n}")
        encryption = st.text_input(f"Encryption {n+1}", key=f"encryption_{n}")
    connections.append({'from': from_device, 'to': to_device, 'port': port, 'protocol': protocol, 'encryption': encryption})

if st.button('Generate Network Diagram'):
    if devices and connections:
        result = create_network_diagram(devices, connections)
        st.text("Here is your network diagram code:")
        st.code(result)
    else:
        st.warning("Please add devices and connections to generate the diagram.")
