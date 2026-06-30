---
sidebar_position: 3
sidebar_label: "Configure Conference Inputs"
---

# Configure Conference inputs for the Pexip Add-on for Splunk

**Description:** Conference inputs enable collection of conference data.

## Pre-Requirements

Before you enable inputs, complete the previous steps in the configuration process:

- [Configure an integration application in Pexip Infinity for the Pexip Add-on for Splunk](./configure_pexip.md)
- [Configure an account in the Pexip Add-on for Splunk](./configure_account.md)

Configure your inputs on the Splunk platform instance responsible for collecting data for this add-on, usually a heavy forwarder. You can configure inputs using Splunk Web (recommended) or using the configuration files.

## Configure inputs using Splunk Web

Configure your inputs using Splunk Web on the Splunk platform instance responsible for collecting data for this add-on, usually a heavy forwarder.

1. In the Pexip Add-on for Splunk, select **Inputs > Create New Input > Conference**.
2. Enter the parameter values using information provided in the input parameter table below.
3. Select **Add**.
4. Verify that data is successfully arriving by running the following searches on your search head:

```bash
    sourcetype=pexip:*:conference
```

If you do not see any events, check the [Troubleshooting](../troubleshoot/troubleshooting.md) section.

## Configure inputs in the configuration files

Configure your inputs using the configuration files on the Splunk platform instance responsible for collecting data for this add-on, usually a heavy forwarder.

1. Create `$SPLUNK_HOME/etc/apps/pexip_addon_for_splunk/local/inputs.conf`.
2. Add the following stanza.

```
<!-- In-progress Conferences -->
[conference://<active_conference_input_name>]
account = <value>
index = <value>
interval = <value>
service_types = <value1|value2|valueN>
historical_data_enabled = 0

<!-- Ended Conferences / Historical Data -->
[conference://<ended_conference_input_name>]
account = <value>
index = <value>
interval = <value>
service_types = <value1|value2|valueN>
historical_data_enabled = 1
service_name = <value>
duration = <value>
```

3. (Optional) Configure a custom `index`.
4. Restart your Splunk platform instance.
5. Verify that data is successfully arriving by running the following search on your search head:

```bash
    sourcetype=pexip:*:conference
```

If you do not see any events, check the [Troubleshooting](../troubleshoot/troubleshooting.md) section.

## Input Parameters

Each attribute in the following table corresponds to a field in Splunk Web.

|Input name                  |Corresponding field in Splunk Web | Description|
|----------------------------|----------------------------------|------------|
|`input_name`                |Input Name                        |A unique name for your input.|
|`account`                   |Account Name                      |The Pexip account from which you want to gather data.|
|`index`                     |Index                             |The index in which the data should be stored. The default is <code>default</code>.|
|`interval`                  |Interval (seconds)                |Rerun the input after the defined value, in seconds. The default value is <code>300</code>.|
| `service_types`            |Service Type(s)                   |The conference service type(s) to filter data to index against. Set to `All` to disable filtering.|
| `historical_data_enabled ` |Historical data                   |Select to index data about conferences that are no longer in progress. Unselect to index data about currently in progress conferences.|
| `service_name`             |Service Name                      |The name used to refer to the service. Enter a value to index data filtered based on service name.|
| `duration`                 |Duration                          |The duration of the conference in seconds. Enter a value to index data filtered based on conference duration.|

Service Type(s) possible values are taken from the API Schema.