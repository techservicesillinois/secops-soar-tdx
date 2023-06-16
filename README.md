# About

This Splunk SOAR Python application is designed to integrate Splunk SOAR with the TeamDynamix ticketing system. Through this integration, the application streamlines and automates cybersecurity workflows by creating and managing tickets in TeamDynamix directly from the Splunk SOAR platform. This app is particularly useful for Security Operations Centers (SOCs), IT departments, and incident response teams that use Splunk SOAR for orchestrating their security workflows and TeamDynamix for ticket management. By integrating these platforms, the application enables automatic ticket creation and management based on security events, thus speeding up incident response and improving operational efficiency.

## Key Features

- **Creating Tickets**: The application allows you to create new tickets in TeamDynamix through SOAR actions. This can be used to automatically create tickets based on alerts and incidents detected by your security tools.

- **Reassigning Tickets**: The application provides actions to reassign existing TeamDynamix tickets. This feature helps in efficiently managing tickets and ensuring they are handled by the appropriate teams or individuals.

## Dependencies

- **Splunk SOAR**: The application is designed to be deployed on the Splunk SOAR platform (formerly Phantom). 

- **Python 3.9**: The application is built with Python 3.9. The end-of-life date for this Python version is October 31, 2025.

- **tdxlib**: The application relies on the [`tdxlib` Python package](https://github.com/cedarville-university/tdxlib) developed by the University of Cedarville.


## Getting Started

Please follow the instructions in the [Manual Deployment](#manual-deployment), [Automated Deployment](#automated-deployment), and [Configuring in SOAR](#configuring-in-soar) sections to set up and configure the application in your Splunk SOAR instance.

After configuring the application, it's recommended to [test the connectivity](#testing-connectivity) to the TeamDynamix ticketing system to ensure that the application is properly configured and able to communicate with its remote endpoint.

## Support

This product is supported by Cybersecurity on a best-effort basis.

As of the last update to this README, the expected End-of-Life and End-of-Support dates of this product are October 2025.

End-of-Life was decided upon based on these dependencies:

    - Python 3.9 (31 October 2025)
    - Splunk SOAR Cloud (Unknown)

## Manual Deployment

Set the environment variables `SOAR_TOKEN` and `SOAR_HOSTNAME`, then run `make deploy`.

## Automated Deployment

Alternately, fork the repository and add the token as `CICD_GITHUB_AUTOMATION` and the URL as `SOAR_URL` to use GitHub Actions for automated deployment.
