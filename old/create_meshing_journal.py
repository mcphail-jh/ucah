import ansys.fluent.core as pyfluent

# Launch Fluent in meshing mode with the GUI
meshing_session = pyfluent.launch_fluent(mode="meshing", show_gui=True)



# Start recording a Python journal file
meshing_session.journal.start(file_name="meshing_journal.py")

# keep window open until a key is pressed
input()

# end and write to journal
meshing_session.journal.stop()
