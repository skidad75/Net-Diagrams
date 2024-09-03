import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import io

# Set up OpenAI API key securely (if needed)
# openai.api_key = st.secrets["openai_key"]

def create_network_diagram(network_devices, network_connections):
    # Create a new graph
    G = nx.Graph()

    # Add nodes (devices)
    for device in network_devices:
        G.add_node(device['name'], device_type=device['type'])

    # Add edges (connections)
    for conn in network_connections:
        G.add_edge(conn['from'], conn['to'], port=conn['port'], protocol=conn['protocol'], encryption=conn['encryption'])

    # Create a layout for our nodes 
    pos = nx.spring_layout(G)

    # Create a new figure
    fig, ax = plt.subplots(figsize=(12, 8))

    # Draw the graph
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=3000, font_size=8, font_weight='bold')

    # Add edge labels
    edge_labels = nx.get_edge_attributes(G, 'port')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    # Add a title
    plt.title("Network Diagram", fontsize=16)

    return fig

# Streamlit interface
st.set_page_config(page_title="NetDiagram Engineering Diagrams", layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("Network Diagram Generator 🤖")

# Initialize session state for devices and connections
if 'network_devices' not in st.session_state:
    st.session_state.network_devices = []
if 'network_connections' not in st.session_state:
    st.session_state.network_connections = []

# Add device form
with st.form(key='add_device_form'):
    device_type = st.text_input("Device Type")
    device_name = st.text_input("Device Name")
    if st.form_submit_button("Add Device"):
        st.session_state.network_devices.append({"type": device_type, "name": device_name})
        st.success(f"Added {device_type} named {device_name}")

# Add connection form
with st.form(key='add_connection_form'):
    from_device = st.selectbox("From Device", [d['name'] for d in st.session_state.network_devices])
    to_device = st.selectbox("To Device", [d['name'] for d in st.session_state.network_devices])
    port = st.text_input("Port")
    protocol = st.text_input("Protocol")
    encryption = st.text_input("Encryption")
    if st.form_submit_button("Add Connection"):
        st.session_state.network_connections.append({
            "from": from_device,
            "to": to_device,
            "port": port,
            "protocol": protocol,
            "encryption": encryption
        })
        st.success(f"Added connection from {from_device} to {to_device}")

# Display current devices and connections
st.subheader("Current Devices")
for device in st.session_state.network_devices:
    st.write(f"{device['type']} - {device['name']}")

st.subheader("Current Connections")
for conn in st.session_state.network_connections:
    st.write(f"{conn['from']} to {conn['to']} using port {conn['port']} over {conn['protocol']} with {conn['encryption']} encryption")

# Generate diagram button
if st.button('Generate Network Diagram'):
    if st.session_state.network_devices and st.session_state.network_connections:
        fig = create_network_diagram(st.session_state.network_devices, st.session_state.network_connections)
        
        # Display the diagram
        st.pyplot(fig)
        
        # Create PDF for download
        pdf_buffer = io.BytesIO()
        fig.savefig(pdf_buffer, format='pdf', bbox_inches='tight')
        pdf_buffer.seek(0)
        
        # Add print button for PDF export
        st.download_button(
            label="Print Network Diagram (PDF)",
            data=pdf_buffer,
            file_name="network_diagram.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Please add devices and connections to generate the diagram.")