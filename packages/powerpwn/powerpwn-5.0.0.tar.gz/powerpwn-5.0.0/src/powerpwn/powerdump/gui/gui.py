import logging
import os
import pathlib
import subprocess  # nosec

from flask import Flask

from powerpwn.cli.const import LOGGER_NAME
from powerpwn.powerdump.gui.prep import (
    env_resources_table_by_resource_type_wrapper,
    env_resources_table_wrapper,
    flt_connection_table_wrapper,
    flt_resource_wrapper,
    full_canvasapps_table_wrapper,
    full_connection_table_wrapper,
    full_connectors_table_wrapper,
    full_logic_flows_table_wrapper,
    full_resources_table_wrapper,
    register_specs,
)


class Gui:
    def run(self, cache_path: str) -> None:

        # run file browser
        subprocess.Popen(
            ["python", "src/powerpwn/common/file_browser/app.py", cache_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True
        )  # nosec

        # check if cache path exists
        if not os.path.exists(cache_path):
            logger = logging.getLogger(LOGGER_NAME)
            logger.error(f"Cache path {cache_path} does not exist")
            return
        # run resources flask app
        app = Flask(__name__, template_folder=self.__get_template_full_path())
        register_specs(app=app, cache_path=cache_path)
        app.route("/")(full_resources_table_wrapper(cache_path=cache_path))
        app.route("/env/<env_id>")(env_resources_table_wrapper(cache_path=cache_path))
        app.route("/env/<env_id>/<resource_type>")(env_resources_table_by_resource_type_wrapper(cache_path=cache_path))
        app.route("/credentials")(full_connection_table_wrapper(cache_path=cache_path))
        app.route("/automation")(full_logic_flows_table_wrapper(cache_path=cache_path))
        app.route("/app/")(full_canvasapps_table_wrapper(cache_path))
        app.route("/connector/")(full_connectors_table_wrapper(cache_path))
        app.route("/credentials/<connector_id>/")(flt_connection_table_wrapper(cache_path=cache_path))
        app.route("/env/<env_id>/<resource_type>/<resource_id>")(flt_resource_wrapper(cache_path=cache_path))

        logger = logging.getLogger(LOGGER_NAME)
        logger.info("Application is running on http://127.0.0.1:5000")

        # turn off server logs
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)

        app.run()

    def __get_template_full_path(self) -> str:
        return os.path.join(pathlib.Path(__file__).parent.resolve(), "templates")
