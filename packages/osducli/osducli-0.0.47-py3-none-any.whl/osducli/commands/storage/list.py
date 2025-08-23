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

"""Schema service get command"""

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_STORAGE_URL


# click entry point
@click.command(cls=CustomClickCommand)
@click.option("-k", "--kind", required=True, help="Get records by kind")
@handle_cli_exceptions
@command_with_output("results")
def _click_command(state: State, kind: str):
    """List records"""
    return list_records(state, kind)


def list_records(state: State, kind: str):
    """List records

    Args:
        state (State): Global state
        kind (str): Kind of records
    """
    connection = CliOsduClient(state.config)

    url = "query/records?kind=" + kind
    json = connection.cli_get_returning_json(CONFIG_STORAGE_URL, url)
    return json
