---
sidebar_position: 2
sidebar_label: "Configure an Account"
---

# Configure an Account in the Pexip Add-on for Splunk

You must configure at least one account in the Pexip Add-on for Splunk.

**Prerequisite:** Before you create an account, complete the previous step in the configuration process:

- [Configure an integration application in Pexip Infinity for the Pexip Add-on for Splunk](./configure_pexip.md)
- Make sure that port 443 is open to allow the Pexip Add-on for Splunk to communicate with the Pexip Infinity management API.

## Set up the add-on using Splunk Web

1. Go to the Splunk Web home screen.
2. Select *Pexip Add-on for Splunk* in the left navigation banner.
3. Select the **Configuration** tab.
4. Under the *Account* section, select on *Add* and fill in the fields. Use the parameters you configured for the application (see [Configure an integration application in Pexip Infinity for the Pexip Add-on for Splunk](./configure_pexip.md)) where:

   - **Name** is the name given to the Account.
   - **Hostname** is the Pexip hostname (e.g. `mydomain.pexip`).
   - **Authentication Type** supports HTTP Basic and OAuth2 for Pexip. Depending on the selection, the following fields must be entered.
     - [Basic] **Username** is the username used to authenticate at Pexip.
     - [Basic] **Password** is the password used to authenticate at Pexip.
     - [OAuth2] **Client Id** is the Client ID from the registered application within Pexip.
     - [OAuth2] **Client Secret** is the registered application private key for the corresponding application.
     - [OAuth2] **Endpoint** is the domain name used for the token acquisition. Example: `yourdomain.login.pexip.com`. It could match the `Hostname`.

5. Select **Add** to add the account to your local configuration.
