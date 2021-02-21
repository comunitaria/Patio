
# Patio Smart Community Brain

This repository contains the software expected to be running on Smart Community Brain, the IOT Hub developed by [Supervecina](https://www.supervecina.com) . It is currently using Raspberry Pi hardware, but can be replaced by an Omega2 LTE or similar.

## Brief code organization overview:
- MAM client is a process listening to new messages from EnergyManager to be published to IOTA's MAM channels, returning the transaction address to allow future queries and verification.

- EnergyManager contains the EnergyMonitor, that periodically monitors the generated and consumed energy in a community.

- start_scb script setups the virtualenv, installs npm packages, and launch both processes mentioned above.

- django_app contains the app that must be plugged into the backend for SaaS integration.

## R+D

Given that each HOA (Homeowner Association) can be treated as a decentralized autonomous organization (DAO), and taking advantage of the IoT devices flexibility and ease of adoption, we are exploring the integration of the Smart Community Brain with projects like [Aragon](https://aragon.org/) (an open source software that allows for the creation and management of decentralized organizations). Using Aragon platform we can improve the HOA management tools combining them with DLTs for critical use cases (votings, incidence reporting, ...). Interaction with other blockchains (like FOAM) can also be achieved through the Cosmos Network.

This way, our Smart Community Brain will be able to:
- monitor and track energy production/consumption
- connect with FOAM beacons and zone anchors
- manage automatic door accesses 
- monitor lifts status and mandatory periodical service
- monitor water consumption

Then, it will impact collected data on DLT technologies (this way we avoid cons of local storage, connection availability, etc.).  
Features can be expanded by connecting the hub to our SaaS, where data can be automatically analyzed with trending algorithms to provide customized services.

