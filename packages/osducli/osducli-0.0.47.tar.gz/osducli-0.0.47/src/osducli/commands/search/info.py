#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Search info command"""

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import handle_cli_exceptions
from osducli.commands.search._const import (
    SEARCH_DOCUMENTATION,
    SEARCH_SERVICE_NAME,
    SEARCH_STATUS_PATH,
    SEARCH_SWAGGER_PATH,
)
from osducli.config import CONFIG_SEARCH_URL
from osducli.util.service_info import info


# click entry point
@click.command(cls=CustomClickCommand)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State) -> dict:
    """Information about the service"""
    return info(
        state,
        SEARCH_SERVICE_NAME,
        CONFIG_SEARCH_URL,
        SEARCH_STATUS_PATH,
        SEARCH_SWAGGER_PATH,
        SEARCH_DOCUMENTATION,
    )
