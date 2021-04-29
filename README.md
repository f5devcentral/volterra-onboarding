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

To configure the script please run the following commands:

```bash
pip3 install -r requirements.txt
./cli.py config azure
./cli.py config volterra
```

For more information about each action use the built-in help:

```bash
./cli.py config azure --help
./cli.py config volterra --help
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

## Remove User

The example below removes the yourusername@example.com user to the Volterra console.

```bash
./cli.py remove yourusername@example.com --tenant mytenant
```

## Remove Group

The example below adds all users of the SRE group to the Volterra console.

```bash
./cli.py remove SRE --tenant mytenant
```

For more information about each action use the built-in help:

```bash
./cli.py --help
./cli.py add --help
./cli.py remove --help
./cli.py config --help
```

# Troubleshoot

You can increase the logging level by running the following config command:

```bash
./cli.py config loglevel
```

Supported log levels are:

- CRITICAL
- ERROR
- WARNING
- INFO
- DEBUG

# Additional Scripts

### AD Group Compare

This script will compare the users in the Voltera Tenant Console versus an Active Directory Group. The script will display the users to are missing from the Azure AD group.

```bash
./ad_group_compare.py --help
./ad_group_compare.py --name SRE --tenant mytenant
```

# Running as a Kubernetes Job

### Create Secrets

The CLI needs the following secrets for the docker container to run correctly:

- Azure AD Application Client ID
- Azure AD Application Secret
- Azure AD Tenant ID
- Volterra VoltConsole Access Token

Run the following commands to create these secrets:

```bash
export KUBECONFIG=<your k8s config file>
export CLIENT_ID=<your azure ad app client id>
export CLIENT_SECRET=<your azure ad app secret>
export TENANT_ID=<your azure ad tenant id>
export VOLT_TOKEN=<your voltconsole access token>
kubectl create secret generic volterra-sso \
    --from-literal=aad-client-id=$CLIENT_ID \
    --from-literal=aad-client-secret=$CLIENT_SECRET \
    --from-literal=aad-tenant=$TENANT_ID \
    --from-literal=volt-token=$VOLT_TOKEN
```

## Support

For support, please open a GitHub issue. Note, the code in this repository is community supported and is not supported by F5 Networks. For a complete list of supported projects please reference [SUPPORT.md](SUPPORT.md).

## Community Code of Conduct

Please refer to the [F5 DevCentral Community Code of Conduct](code_of_conduct.md).

## License

[Apache License 2.0](LICENSE)

## Copyright

Copyright 2014-2020 F5 Networks Inc.

### F5 Networks Contributor License Agreement

Before you start contributing to any project sponsored by F5 Networks, Inc. (F5) on GitHub, you will need to sign a Contributor License Agreement (CLA).

If you are signing as an individual, we recommend that you talk to your employer (if applicable) before signing the CLA since some employment agreements may have restrictions on your contributions to other projects.
Otherwise by submitting a CLA you represent that you are legally entitled to grant the licenses recited therein.

If your employer has rights to intellectual property that you create, such as your contributions, you represent that you have received permission to make contributions on behalf of that employer, that your employer has waived such rights for your contributions, or that your employer has executed a separate CLA with F5.

If you are signing on behalf of a company, you represent that you are legally entitled to grant the license recited therein.
You represent further that each employee of the entity that submits contributions is authorized to submit such contributions on behalf of the entity pursuant to the CLA.
