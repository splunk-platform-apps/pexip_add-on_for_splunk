import json
import logging

import import_declare_test  # noqa: F401
from solnlib import conf_manager, log
from solnlib.conf_manager import InvalidHostnameError, InvalidPortError
from solnlib.modular_input import checkpointer
from solnlib.utils import is_true
from splunklib import modularinput as smi
from datetime import datetime, timedelta, timezone
from pexip_client import PexipClient


ADDON_NAME = "pexip_addon_for_splunk"


def logger_for_input(input_name: str) -> logging.Logger:
    return log.Logs().get_logger(f"{ADDON_NAME.lower()}_{input_name}")


def get_account(session_key: str, account_name: str):
    cfm = conf_manager.ConfManager(
        session_key,
        ADDON_NAME,
        realm=f"__REST_CREDENTIAL__#{ADDON_NAME}#configs/conf-pexip_addon_for_splunk_account",
    )
    account_conf_file = cfm.get_conf("pexip_addon_for_splunk_account")
    return account_conf_file.get(account_name)


def validate_input(definition: smi.ValidationDefinition):
    return


def stream_events(inputs: smi.InputDefinition, event_writer: smi.EventWriter):
    # inputs.inputs is a Python dictionary object like:
    # {
    #   "conference://<input_name>": {
    #     "account": "<account_name>",
    #     "disabled": "0",
    #     "host": "$decideOnStartup",
    #     "index": "<index_name>",
    #     "interval": "<interval_value>",
    #     "python.version": "python3",
    #   },
    # }
    for input_name, input_item in inputs.inputs.items():
        normalized_input_name = input_name.split("/")[-1]
        logger = logger_for_input(normalized_input_name)
        try:
            session_key = inputs.metadata["session_key"]
            kvstore_checkpointer = checkpointer.KVStoreCheckpointer(
                "conference_checkpointer",
                session_key,
                ADDON_NAME,
            )
            log_level = conf_manager.get_log_level(
                logger=logger,
                session_key=session_key,
                app_name=ADDON_NAME,
                conf_name="pexip_addon_for_splunk_settings",
            )
            logger.setLevel(log_level)
            try:
                proxy_config = conf_manager.get_proxy_dict(
                    logger=logger,
                    session_key=session_key,
                    app_name=ADDON_NAME,
                    conf_name="pexip_addon_for_splunk_settings",
                )
            # Handle invalid port case
            except InvalidPortError as e:
                logger.error(f"Proxy configuration error: {e}")

            # Handle invalid hostname case
            except InvalidHostnameError as e:
                logger.error(f"Proxy configuration error: {e}")

            log.modular_input_start(logger, normalized_input_name)

            account = get_account(session_key, input_item.get("account"))
            s_types = input_item.get("service_types")
            service_types = [] if "*" in s_types else s_types.split("|")
            historical_data = is_true(input_item.get("historical_data_enabled"))
            service_name = input_item.get("service_name", None)
            duration = input_item.get("duration", -1)

            # hostname = get_account_property(session_key, account, "hostname")
            # auth_type = get_account_property(session_key, account, "auth_type")

            logger.debug("Initializing Pexip Client")
            client = PexipClient(logger, account, proxy_config)

            checkpointer_key_name = input_name.split("/")[-1]
            # if we don't have any checkpoint, we default it to 7 days ago
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            current_checkpoint = (
                kvstore_checkpointer.get(checkpointer_key_name)
                or seven_days_ago.timestamp()
            )

            logger.debug("Requesting to fetch conference data")
            data = client.get_conference_data(
                datetime.fromtimestamp(current_checkpoint),
                service_types,
                service_name,
                duration,
                not historical_data,
            )

            event_counter = 0
            resource = "history" if historical_data else "status"
            sourcetype = f"pexip:{resource}:conference"
            for object in data:
                event_time_epoch = client.to_datetime(object["start_time"]).timestamp()
                event_writer.write_event(
                    smi.Event(
                        data=json.dumps(object, ensure_ascii=False, default=str),
                        index=input_item.get("index"),
                        sourcetype=sourcetype,
                        time=event_time_epoch,
                    )
                )
                event_counter += 1

            # Updating checkpoint if data was indexed to avoid losing info
            if event_counter > 0:
                logger.debug(f"Indexed '{event_counter}' events")
                new_checkpoint = datetime.now(timezone.utc).timestamp()
                logger.debug(f"Updating checkpointer to {new_checkpoint}")
                kvstore_checkpointer.update(checkpointer_key_name, new_checkpoint)

            log.events_ingested(
                logger,
                input_name,
                sourcetype,
                event_counter,
                input_item.get("index"),
                account=input_item.get("account"),
            )
            log.modular_input_end(logger, normalized_input_name)
        except Exception as e:
            log.log_exception(
                logger,
                e,
                "IngestionError",
                msg_before=f"Exception raised while ingesting data for input: {normalized_input_name}",
            )
