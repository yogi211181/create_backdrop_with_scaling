Dynamic Backdrop with Scaling and Finalization
This Nuke script creates a dynamic backdrop node that:

Scales and Aligns Nodes Dynamically:

Nodes inside the backdrop automatically realign and scale relative to the backdrop's size when resized.
Nodes dragged outside the backdrop are unaffected by scaling.
Nodes regain scaling behavior when moved back into the backdrop.
Randomized Backdrop Colors:

Each backdrop gets a unique random color for easy visual distinction.
Finalize the Setup:

A "Break Connection" button in the User tab allows users to finalize the current layout by:
Removing the dynamic scaling behavior.
Freezing nodes in their current positions.
Clearing all internal connections and stored data.
Features:
Dynamic Scaling: Automatically adjusts node positions inside the backdrop when resized.
Node Inclusion/Exclusion: Nodes dragged outside the backdrop are ignored during scaling.
Finalization: Simplifies node setups by breaking dynamic connections when no further changes are needed.
Shortcut Key:
Use Ctrl+Shift+B to create a dynamic backdrop around selected nodes.
