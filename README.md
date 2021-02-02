# Volterra Onboarding 
This project contains scripts to help onboard user(s) to a Volterra Tenant Console

# Requirements
This script requires
- Python 3
- A [Registered application](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app) with Azure Active Directory
    - You will need to [grant the following API permissions](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-configure-app-access-web-apis):
        - GroupMember.Read.All(Delegated for CLI, Application for FaaS)
        - User.Read (Delegated)
    - Add a [redirect URL](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app#configure-platform-settings) of:
        - msalce4fb564-dee3-4977-8447-73d95d588593://auth
        - http://localhost:51691
    - Copy the following settings from the app: 
        - Azure Application (Client) ID
        - Azure Diretory (Tenant) ID
- [Volterra API Key](https://www.volterra.io/docs/how-to/user-mgmt/credentials?query=Generate%20API%20Tokens)

# Setup
To use this script you will need need:

To configure the script please run the following commands:
```bash
pip3 install -r requirements.txt
./cli.py config azure
./cli.py config volterra
```

# Usage
The script can add an individual user or all users in an AD group to the Volterra console.

## Add User
The example below adds the yourusername@example.com user to the Volterra console.
```bash
./cli.py add yourusername@example.com --tenant mytenant
```

## Add Group
The example below adds all users of the SRE group to the Volterra console.
```bash
./cli.py add SRE --tenant mytenant
```