# Volterra Onboarding 
This project contains scripts to help onboard user(s) to a Volterra Tenant Console

# Requirements
This script requires
- Python 3
- Azure Application ID (Client ID)
- Volterra API Key

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

# Azure AD Application 
You will need an Azure AD application with the following API permissions:
- GroupMember.Read.All(Delegated for CLI, Application for FaaS)
- User.Read (Delegated)