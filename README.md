# Comunitaria's Smart Community Brain

- This software is expected to be running on Smart Community Brain (Raspberry Pi).

- MAM client is a process listening to new messages from EnergyManager to be published to MAM.

- EnergyManager contains the EnergyMonitor, that periodically monitors the generated and consumed energy in a community.

- start_scb script setups the virtualenv, installs npm packages, and launch both processes.

- django_app contains the app that must be plugged into the backend

