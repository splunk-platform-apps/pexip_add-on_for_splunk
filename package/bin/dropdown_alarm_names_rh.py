import import_declare_test
from solnlib import log
import splunk.admin as admin
import logging

ADDON_NAME = "pexip_addon_for_splunk"
logger = log.Logs().get_logger(f"{ADDON_NAME.lower()}_list_alarm_names_rh")
logger.info("file_is getting executed")

class DropDownAlarmNamesHandler(admin.MConfigHandler):
    """
    Fetch the alarm names dynamically from the schema.
    TODO add the dynamic fetching of data. Requires authentication.
    """

    def setup(self):
        # Commented code from:
        # https://github.com/splunk/addonfactory-ucc-generator/blob/develop/tests/testdata/test_addons/package_global_config_everything/package/bin/dependent_dropdown.py
        # https://github.com/splunk/addonfactory-ucc-generator/blob/develop/tests/testdata/test_addons/package_global_config_everything/globalConfig.json#L1150

        # if self.requestedAction == admin.ACTION_LIST:
        #     # Add required args in supported args
        #     self.supportedArgs.addReqArg("input_one_radio")
        return

    def handleList(self, confInfo):
        confInfo["Capacity Exhausted"] = ("Capacity Exhausted", "capacity_exhausted")
        confInfo["Licenses Exhausted"] = ("Licenses Exhausted", "licenses_exhausted")
        confInfo["Licenses Expiring"] = ("Licenses Expiring", "licenses_expiring")
        confInfo["Syslog Inaccessible"] = ("Syslog Inaccessible", "syslog_inaccessible")
        confInfo["Management Node Exhausted"] = ("Management Node Exhausted", "management_node_exhausted")
        confInfo["Trusted CA Expiring"] = ("Trusted CA Expiring", "trustedca_expiring")
        confInfo["TLS Certificate Expiring"] = ("TLS Certificate Expiring", "tls_certificate_expiring")
        confInfo["TLS Certificate Chains"] = ("TLS Certificate Chains", "tls_certificate_chains")
        confInfo["TLS Certificate Missing"] = ("TLS Certificate Missing", "tls_certificate_missing")
        confInfo["CPU Not Supported"] = ("CPU Not Supported", "cpu_not_supported")
        confInfo["NTP Not Synchronised"] = ("NTP Not Synchronised", "ntp_not_synchronised")
        confInfo["Bursting Error"] = ("Bursting Error", "bursting_error")
        confInfo["Bursting Missing Pexip Node"] = ("Bursting Missing Pexip Node", "bursting_missing_pexip_node")
        confInfo["Bursting No Location Overflow"] = ("Bursting No Location Overflow", "bursting_no_location_overflow")
        confInfo["Bursting Unauthorized Instance Failure"] = ("Bursting Unauthorized Instance Failure", "bursting_unauthorized_instance_failure")
        confInfo["Bursting Unauthorized Region Failure"] = ("Bursting Unauthorized Region Failure", "bursting_unauthorized_region_failure")
        confInfo["Bursting Authentication Failure"] = ("Bursting Authentication Failure", "bursting_authentication_failure")
        confInfo["Configuration Sync Failure"] = ("Configuration Sync Failure", "confuration_sync_failure")
        confInfo["Connectivity Lost"] = ("Connectivity Lost", "connectivity_lost")
        confInfo["TLS Certificate Missing Management"] = ("TLS Certificate Missing Management", "tls_certificate_missing_management")
        confInfo["Irregular Pulse"] = ("Irregular Pulse", "irregular_pulse")
        confInfo["Scheduling Connection Failure"] = ("Scheduling Connection Failure", "scheduling_connection_failure")
        confInfo["CPU Deprecated"] = ("CPU Deprecated", "cpu_deprecated")
        confInfo["IO High Latency"] = ("IO High Latency", "io_high_latency")
        confInfo["Autobackup Upload Failed"] = ("Autobackup Upload Failed", "autobackup_upload_failed")
        confInfo["Possible VOIP Scanner IPS Blocked"] = ("Possible VOIP Scanner IPS Blocked", "possible_voip_scanner_ips_blocked")
        confInfo["Service Access Quarantined"] = ("Service Access Quarantined", "service_access_quarantined")
        confInfo["LDAP Sync Failure"] = ("LDAP Sync Failure", "ldap_sync_failure")
        confInfo["MJX Google Gatherer Failure"] = ("MJX Google Gatherer Failure", "mjx_google_gatherer_failure")
        confInfo["MJX Exchange Gatherer Failure"] = ("MJX Exchange Gatherer Failure", "mjx_exchange_gatherer_failure")
        confInfo["MJX Graph Gatherer Failure"] = ("MJX Graph Gatherer Failure", "mjx_graph_gatherer_failure")
        confInfo["MJX Endpoint Configurator Failure"] = ("MJX Endpoint Configurator Failure", "mjx_endpoint_confurator_failure")
        confInfo["MJX Meeting Processor Failure"] = ("MJX Meeting Processor Failure", "mjx_meeting_processor_failure")
        confInfo["MJX Poly Failure"] = ("MJX Poly Failure", "mjx_poly_failure")
        confInfo["Eventsink Maximum Backoff"] = ("Eventsink Maximum Backoff", "eventsink_maximum_backoff")
        confInfo["Eventsink Maximum Posts"] = ("Eventsink Maximum Posts", "eventsink_maximum_posts")
        confInfo["MJX Webex Failure"] = ("MJX Webex Failure", "mjx_webex_failure")
        confInfo["Scheduled Maintenance Event Freeze"] = ("Scheduled Maintenance Event Freeze", "scheduled_maintenance_event_freeze")
        confInfo["Scheduled Maintenance Event Redeploy"] = ("Scheduled Maintenance Event Redeploy", "scheduled_maintenance_event_redeploy")
        confInfo["Scheduled Maintenance Event Preempt"] = ("Scheduled Maintenance Event Preempt", "scheduled_maintenance_event_preempt")
        confInfo["Azure Teams Connector Scheduled Scaling Failure"] = ("Azure Teams Connector Scheduled Scaling Failure", "azure_teamsconnector_scheduledscaling_failure")
        confInfo["Azure Teams Connector Scheduled Scaling Not Enough Instances Failure"] = ("Azure Teams Connector Scheduled Scaling Not Enough Instances Failure", "azure_teamsconnector_scheduledscaling_notenoughinstances_failure")
        confInfo["Azure Teams Connector Scheduled Scaling Endpoint Not Found"] = ("Azure Teams Connector Scheduled Scaling Endpoint Not Found", "azure_teamsconnector_scheduledscaling_endpoint_not_found")
        confInfo["Integrity Error"] = ("Integrity Error", "integrity_error")
        confInfo["Azure Key Vault Certificate Expiring"] = ("Azure Key Vault Certificate Expiring", "azure_key_vault_certificate_expiring")
        confInfo["Azure Key Vault Certificate Expired"] = ("Azure Key Vault Certificate Expired", "azure_key_vault_certificate_expired")
        confInfo["GMS Gateway Token Expiring"] = ("GMS Gateway Token Expiring", "gms_gateway_token_expiring")
        # if self.callerArgs.data["input_one_radio"] == ["yes"]:
        #     confInfo["affirmation"] = ("key", "value")
        # else:
        #     confInfo["denial"] = ("key_n", "value_n")

if __name__ == '__main__':
    logging.getLogger().addHandler(logging.NullHandler())
    admin.init(DropDownAlarmNamesHandler, admin.CONTEXT_NONE)