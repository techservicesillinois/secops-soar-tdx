# About


## Support

This product is supported by Cybersecurity on a best-effort basis.

As of the last update to this README, the expected End-of-Life and End-of-Support dates of this product are October 2025.

End-of-Life was decided upon based on these dependencies:

    - Python 3.9 (31 October 2025)
    - Splunk SOAR Cloud (Unknown)

## Manual Deployment

Set the environment variables `SOAR_TOKEN` and `SOAR_URL`, then run `make deploy`.

## Automated Deployment

Alternately, fork the repository and add the token as `CICD_GITHUB_AUTOMATION` and the URL as `SOAR_URL` to use GitHub Actions for automated deployment.

## Configuring in SOAR

1. Create an API access token in your instance of [BHR Site][3].
2. [Deploy this app](#manual-deployment) to your Splunk SOAR instance.

3. After deployment, find the app in `Unconfigured Apps`, hit `Configure App`, and set the necessary `Environment Variables` under `Advanced`.

This app requires the same two environment variables as [BHR Client][4]:

- Add the full URL to your BHR server as `BHR_HOST`.
- Add the access token you created to `BHR_TOKEN`.
