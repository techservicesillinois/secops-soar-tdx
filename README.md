# About

This Splunk SOAR Python application is designed to integrate Splunk SOAR with the TeamDynamix ticketing system. Through this integration, the application streamlines and automates cybersecurity workflows by creating and managing tickets in TeamDynamix directly from the Splunk SOAR platform. This app is particularly useful for Security Operations Centers (SOCs), IT departments, and incident response teams that use Splunk SOAR for orchestrating their security workflows and TeamDynamix for ticket management. By integrating these platforms, the application enables automatic ticket creation and management based on security events, thus speeding up incident response and improving operational efficiency.

## Key Features

- **Creating Tickets**: The application allows you to create new tickets in TeamDynamix through SOAR actions. This can be used to automatically create tickets based on alerts and incidents detected by your security tools.

  + Parameters:
    + priority: Ticket priority
      + Low
      + Medium
      + High
      + Emergency
      + VIP
      + IT Pro
    + requestor: Requestor User ID
    + title: Ticket title
    + description: Ticket description
    + type: Ticket type
      + For CSOC tickets this should be 'CSOC'
    + notify: If selected, notify requestor and responsible
    + status: Ticket Status
      + New
      + Open
      + In Process
      + Awaiting Response
      + Resolved
      + Closed
      + Cancelled
      + On Hold
      + Duplicate
      + Spam
    + formid: Form of the ticket, default is 'UIUC-TechSvc-CSOC Incidents'
      + [UIUC-TechSvc-CSOC Incidents] (ID 1069)
      + [UIUC-TechSvc-CSOC Informational] (ID 1070)
      + [UIUC-TechSvc-CSOC Events] (ID 1068)
      + [UIUC-TechSvc-CSOC Processes] (ID 1071)
    + severity: 'UIUC-TechSvc-CSOC Incident Severity'
      + Low
      + Medium
      + High
      + Critical
      + To Be Determined
      + Non-Event

- **Reassigning Tickets**: The application provides actions to reassign existing TeamDynamix tickets. This feature helps in efficiently managing tickets and ensuring they are handled by the appropriate teams or individuals.

  + Action: reassign group
    + parameters
      + ticket id: The ticket ID
      + responsible: name of the group to assign responsibility to
        + Example: 'Cybersecurity Developers' or 'Cybersecurity Engineers'

  + Action: reassign user
    + parameters
      + ticket id: The ticket ID
      + responsible: NetID or email of user responsible

## Dependencies

- **Splunk SOAR**: The application is designed to be deployed on the Splunk SOAR platform (formerly Phantom).

- **Python 3.9**: The application is built with Python 3.9. The end-of-life date for this Python version is October 31, 2025.

- **tdxlib**: The application relies on the [`tdxlib` Python package](https://github.com/cedarville-university/tdxlib) developed by the University of Cedarville.

## Getting Started

Follow the instructions in the [Manual Deployment](#manual-deployment) or [Automated Deployment](#automated-deployment) sections to install the application, then follow [Configuring in SOAR](#configuring-in-soar) to connect to your TDX instance.

## Configuring in SOAR

To configure the TDX SOAR app to connect to your TeamDynamix instance, add an asset configuration to the TDX SOAR app with the following values:

- Your `Organization Name` if TeamDynamix hosts your TDX instance **or** the `Endpoint URL` of your TDX instance if self-hosted.
- An API `username` and `password` from configured in your TDX instance
- The `AppID` of the application within TDX that you need to interact with from SOAR
- The `timezone` your TDX server runs in
- Your preferred `logging level` for the TDX SOAR app (ERROR is recommended)

Use the `Test Connectivity` button in SOAR to verify your settings.

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
