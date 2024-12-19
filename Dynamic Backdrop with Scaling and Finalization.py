import nuke
import random

def create_backdrop_with_scaling():
    """
    Creates a backdrop around selected nodes, centers them, and dynamically scales
    their positions relative to the backdrop as it is resized. Nodes dragged outside
    the backdrop are unaffected by scaling, and a "Break Connection" button lets
    users finalize the setup by removing dynamic behavior.
    """
    # Get the selected nodes
    selected_nodes = nuke.selectedNodes()
    if not selected_nodes:
        nuke.message("No nodes selected. Please select nodes to wrap in a backdrop.")
        return

    # Calculate the bounding box of the selected nodes
    x_positions = [node.xpos() for node in selected_nodes]
    y_positions = [node.ypos() for node in selected_nodes]
    widths = [node.screenWidth() for node in selected_nodes]
    heights = [node.screenHeight() for node in selected_nodes]

    x_min = min(x_positions)
    y_min = min(y_positions)
    x_max = max(x + w for x, w in zip(x_positions, widths))
    y_max = max(y + h for y, h in zip(y_positions, heights))

    # Create the backdrop node
    padding = 50  # Add some padding around the nodes
    backdrop = nuke.createNode("BackdropNode")
    initial_width = (x_max - x_min) + 2 * padding
    initial_height = (y_max - y_min) + 2 * padding

    backdrop["xpos"].setValue(x_min - padding)
    backdrop["ypos"].setValue(y_min - padding)
    backdrop["bdwidth"].setValue(initial_width)
    backdrop["bdheight"].setValue(initial_height)

    # Randomize the backdrop color
    backdrop_color = int(random.random() * 0xFFFFFF) | 0xFF000000  # Ensure the color is opaque
    backdrop["tile_color"].setValue(backdrop_color)

    # Store the node data invisibly
    node_data = {
        node.name(): {
            "relative_x": (node.xpos() - backdrop["xpos"].value()) / initial_width,
            "relative_y": (node.ypos() - backdrop["ypos"].value()) / initial_height,
        }
        for node in selected_nodes
    }

    # Add a hidden knob to store the serialized data
    if "node_data" not in backdrop.knobs():
        knob = nuke.String_Knob("node_data", "")
        knob.setFlag(nuke.INVISIBLE)
        backdrop.addKnob(knob)
    backdrop["node_data"].setValue(str(node_data))  # Store serialized data in the hidden knob

    # Add a "Break Connection" button
    if "break_connection" not in backdrop.knobs():
        button = nuke.PyScript_Knob("break_connection", "Break Connection")
        backdrop.addKnob(button)

    # Define the realign_nodes logic
    def realign_nodes(backdrop):
        """
        Aligns and scales nodes dynamically based on the backdrop's size and position.
        Checks if nodes are inside the backdrop to determine if they should be scaled.
        """
        try:
            # Extract and deserialize node data from the hidden knob
            node_data = eval(backdrop["node_data"].value())
            current_width = backdrop["bdwidth"].value()
            current_height = backdrop["bdheight"].value()

            for node_name, data in node_data.items():
                target_node = nuke.toNode(node_name)
                if target_node:
                    # Check if the node is inside the backdrop
                    node_x = target_node.xpos()
                    node_y = target_node.ypos()
                    backdrop_x = backdrop["xpos"].value()
                    backdrop_y = backdrop["ypos"].value()
                    backdrop_width = backdrop["bdwidth"].value()
                    backdrop_height = backdrop["bdheight"].value()

                    if (
                        backdrop_x <= node_x <= backdrop_x + backdrop_width
                        and backdrop_y <= node_y <= backdrop_y + backdrop_height
                    ):
                        # Node is inside the backdrop, apply scaling
                        new_x = backdrop["xpos"].value() + data["relative_x"] * current_width
                        new_y = backdrop["ypos"].value() + data["relative_y"] * current_height
                        target_node.setXpos(int(new_x))
                        target_node.setYpos(int(new_y))
        except Exception as e:
            nuke.message(f"Error while realigning nodes: {e}")

    # Attach the knobChanged callback as an embedded script
    realign_script = f"""
from __main__ import nuke
node = nuke.thisNode()
try:
    import ast
    node_data = ast.literal_eval(node['node_data'].value())
    current_width = node['bdwidth'].value()
    current_height = node['bdheight'].value()

    for node_name, data in node_data.items():
        target_node = nuke.toNode(node_name)
        if target_node:
            node_x = target_node.xpos()
            node_y = target_node.ypos()
            backdrop_x = node['xpos'].value()
            backdrop_y = node['ypos'].value()
            backdrop_width = node['bdwidth'].value()
            backdrop_height = node['bdheight'].value()

            if backdrop_x <= node_x <= backdrop_x + backdrop_width and backdrop_y <= node_y <= backdrop_y + backdrop_height:
                new_x = backdrop_x + data['relative_x'] * current_width
                new_y = backdrop_y + data['relative_y'] * current_height
                target_node.setXpos(int(new_x))
                target_node.setYpos(int(new_y))
except Exception as e:
    nuke.message(f"Error while realigning nodes: {{e}}")
"""
    backdrop["knobChanged"].setValue(realign_script)

    # Embed the Break Connection logic directly in the button
    break_script = """
node = nuke.thisNode()
if 'knobChanged' in node.knobs():
    node['knobChanged'].setValue('')  # Remove the callback
if 'node_data' in node.knobs():
    node['node_data'].setValue('')  # Clear the stored node data
nuke.message('Dynamic scaling connections have been broken.')
"""
    backdrop["break_connection"].setValue(break_script)

# Register the function in the menu with a shortcut key
nuke.menu("Nuke").addCommand("Edit/Create Backdrop with Scaling", create_backdrop_with_scaling, "Ctrl+Shift+B")
