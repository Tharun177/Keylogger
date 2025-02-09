#!/bin/bash

# Create a virtual environment
python3 -m venv keylogger-env

# Activate the virtual environment
source keylogger-env/bin/activate

# Install required packages
pip install pyscreenshot sounddevice pynput

# Deactivate the virtual environment
deactivate

echo "Installation complete. To run the keylogger, activate the virtual environment and run keylogger.py."
echo "source keylogger-env/bin/activate"
echo "python keylogger.py"
