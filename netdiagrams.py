import streamlit as st
import openai

# Set up OpenAI API key securely
openai.api_key = st.secrets["openai_key"]

def create_network_diagram(devices, connections):
    prompt = "Generate a network diagram that includes the following devices and connections:\n"
    for device in devices:
        prompt += f"- {device['type']} named {device['name']}\n"
    prompt += "Connections:\n"
    for conn in connections:
        prompt += f"- {conn['from']} to {conn['to']} using port {conn['port']} over {conn['protocol']} with {conn['encryption']} encryption\n"
    prompt += "The diagram should reflect network engineering standards. Output the diagram as a JSON object."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON diagrams and are a network engineer responsible for creating diagrams and documentation software and systems."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Failed to generate diagram: {str(e)}"

# Streamlit interface
st.set_page_config(page_title="NetDiagram Engineering Diagrams", layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("Network Diagram Generator 🤖")

# Initialize session state for devices and connections
if 'devices' not in st.session_state:
    st.session_state.devices = []
if 'connections' not in st.session_state:
    st.session_state.connections = []

# Add device form
with st.form(key='add_device_form'):
    device_type = st.text_input("Device Type")
    device_name = st.text_input("Device Name")
    if st.form_submit_button("Add Device"):
        st.session_state.devices.append({"type": device_type, "name": device_name})
        st.success(f"Added {device_type} named {device_name}")

# Add connection form
with st.form(key='add_connection_form'):
    from_device = st.selectbox("From Device", [d['name'] for d in st.session_state.devices])
    to_device = st.selectbox("To Device", [d['name'] for d in st.session_state.devices])
    port = st.text_input("Port")
    protocol = st.text_input("Protocol")
    encryption = st.text_input("Encryption")
    if st.form_submit_button("Add Connection"):
        st.session_state.connections.append({
            "from": from_device,
            "to": to_device,
            "port": port,
            "protocol": protocol,
            "encryption": encryption
        })
        st.success(f"Added connection from {from_device} to {to_device}")

# Display current devices and connections
st.subheader("Current Devices")
for device in st.session_state.devices:
    st.write(f"{device['type']} - {device['name']}")

st.subheader("Current Connections")
for conn in st.session_state.connections:
    st.write(f"{conn['from']} to {conn['to']} using port {conn['port']} over {conn['protocol']} with {conn['encryption']} encryption")

# Generate diagram button
if st.button('Generate Network Diagram'):
    if st.session_state.devices and st.session_state.connections:
        result = create_network_diagram(st.session_state.devices, st.session_state.connections)
        st.text("Here is your network diagram JSON:")
        st.json(result)
    else:
        st.warning("Please add devices and connections to generate the diagram.")