---
sidebar_position: 1
sidebar_label: "Configure an integration application in Pexip"
---

# Configure an integration application in Pexip Inifinity for the Pexip Add-on for Splunk

In order to gather data from the Pexip Infinity management API using this add-on, users must authenticate using either OAuth2 or HTTP Basic Authentication, which includes the local Pexip admin username and password, or a valid LDAP username and password.

## HTTP Basic Authentication

* [Managing local administrator authentication](https://docs.pexip.com/admin/managing_admin_local.htm)
* [Managing administrator access via LDAP](https://docs.pexip.com/admin/managing_admin_ldap.htm)

## OAuth2 Authentication

* [Create an appropriate administrator role](#create-an-appropriate-administrator-role).
* [Create a management API OAuth2 client and assign the created administrator role to it](#create-a-management-api-oauth2-client-in-pexip).
* [Configure management API OAuth2 settings](https://docs.pexip.com/admin/managing_API_oauth.htm#api_oauth).

This client securely authenticates the Add-on via the
OAuth2 protocol, so that it can access and gather the data according to the services and permission levels that you specify.

### Create an appropriate administrator role

1. See definition and instructions provided in the [Pexip documentation](https://docs.pexip.com/admin/managing_API_oauth.htm#account_roles)
2. When configuring the administrator role, please set the following [permissions](https://docs.pexip.com/admin/managing_admin_roles.htm#permissions), required for the Pexip Add-on for Splunk.

| Permission name       | Description |
|-----------------------| ----------- |
| `Is an administrator`	| Required for accessing any of the other permissions |
| `May use API`	        | Required to access the Pexip Infinity management API (via api/admin) |
| `May view conference status` | To read conference and participant status |
| `May view logs`              | To read conference and participant history, usage statistics, etc |

### Create a management API OAuth2 Client in Pexip

1. Follow the instructions in the [Pexip documentation](https://docs.pexip.com/admin/managing_API_oauth.htm#create_client/) for the client creation and configuration.

2. When creating your client, <u>make a note of the following parameters</u>. They will be needed to [Configure an Account in the Pexip Add-on for Splunk](./configure_account.md).

    - Entered **Client name** (aka **Client Id** in the Pexip Add-on for Splunk).
    - Generated **Private Key** (aka **Client Secret** in the Pexip Add-on for Splunk).
