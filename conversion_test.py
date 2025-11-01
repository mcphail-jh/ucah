import ansys.fluent.core as pyfluent

# Launch Fluent in meshing mode with the GUI
setup_session = pyfluent.launch_fluent(mode="solver", show_gui=True)


# Start recording a Python journal file
setup_session.journal.start(file_name="setup_journalv1.py")

# keep window open until a key is pressed
input()

# end and write to journal
setup_session.journal.stop()
