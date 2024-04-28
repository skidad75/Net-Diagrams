import streamlit as st
from openai import OpenAI
import os

OpenAI.api_key = st.secrets.openai_key

def create_network_diagram(devices, connections):
    # Building a detailed prompt
    prompt = "Generate a network diagram code that includes the following devices and connections:\n"
    for device in devices:
        prompt += f"- {device['type']} named {device['name']}\n"
    prompt += "Connections:\n"
    for conn in connections:
        prompt += f"- {conn['from']} to {conn['to']} using port {conn['port']} over {conn['protocol']} with {conn['encryption']} encryption\n"
    prompt += "The diagram should reflect network engineering standards."

    try:
        response = client.completions.create(engine="text-davinci-002",
        prompt=prompt,
        max_tokens=250)
        return response.choices[0].text.strip()
    except Exception as e:
        return str(e)

# Streamlit interface
st.title('Network Diagram Generator')

st.subheader('Devices')
# Dynamic input fields for devices
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
