# Copyright 2023
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" This script implements the main function.
"""

import sys
import os
import argparse
import checkov_fix_chart
import datree_fix_chart
import kics_fix_chart
import kubelinter_fix_chart
import kubeaudit_fix_chart
import kubescape_fix_chart
import terrascan_fix_chart
import sonar_fix_chart
import add_functionalities
import generate_docker_run
import count_checks


# Define the argument parser
parser = argparse.ArgumentParser(description='Script to fix Helm Charts based on results from \
                                 security tools and add required functionalities.')

# Add the --check argument
parser.add_argument('--check', action='store_true', help='Fix the chart based on the results \
                                                        of a tool.')
# Add the --add-func argument
parser.add_argument('--add-func', action='store_true', help='Add required functionality to \
                                                            the chart.')

# Add the --add-func argument
parser.add_argument('--docker-run', action='store_true', help='Generate Docker run command')

# Add the --add-func argument
parser.add_argument('--count-checks', action='store_true', help='Count final checks')

# Parse the arguments
args = parser.parse_args()


def main():
    """ The main function.
    """

    # Get chart_folder from ENV
    # For local testing on macOS, add env variables to ~/.zshrc
    chart_folder = os.environ.get("chart_folder")

    tool = os.environ.get("first_tool")
    # tool = os.environ.get("tool")

    # Fix the chart based on the results of a tool
    if args.check:
        # Get ENV variables
        iteration = os.environ.get("iteration")
        result_path = f"results_{iteration}.json"

        if iteration == "1":
            chart_folder = f"templates/{chart_folder}"
        elif iteration == "2" or iteration == "3":
            chart_folder = f"fixed_templates/{chart_folder}"

        # result_path = f"test_files/{tool}_results.json"

        # Check if there are any failed tests
        print(f"tool: {tool}")

        match tool:
            case "checkov": 
                checkov_fix_chart.iterate_checks(chart_folder, result_path)
            case "datree": 
                datree_fix_chart.iterate_checks(chart_folder, result_path)
            case "kics": 
                kics_fix_chart.iterate_checks(chart_folder, result_path)
            case "kubelinter": 
                kubelinter_fix_chart.iterate_checks(chart_folder, result_path)
            case "kubeaudit":
                kubeaudit_fix_chart.iterate_checks(chart_folder, result_path)
            case "kubescape": 
                kubescape_fix_chart.iterate_checks(chart_folder, result_path)
            case "terrascan": 
                terrascan_fix_chart.iterate_checks(chart_folder, result_path)
            case "sonarcloud": 
                sonar_fix_chart.iterate_checks(chart_folder, result_path)
            case _: 
                print("Tool not supported. Exiting..."); sys.exit(1)

    # Add required functionality to the chart
    elif args.add_func:
        json_path = f"functionality_profiles/{chart_folder}/{chart_folder}_functionality.json"
        add_functionalities.iterate_functionalities(chart_folder, json_path, tool)

    # Generate Docker run command from YAML template
    elif args.docker_run:
        resource_path = os.environ.get("resource_path")
        obj_path = os.environ.get("obj_path")
        generate_docker_run.get_docker_run_cmd(chart_folder, resource_path, obj_path)

    # Count final checks
    elif args.count_checks:
        # Get ENV variables
        tool = os.environ.get("second_tool")
        iteration = os.environ.get("iteration")
        result_path = f"results_{iteration}.json"
        count_checks.count_checks(result_path, tool)

    else:
        print("No arguments passed. Exiting...")
        sys.exit(1)


if __name__ == "__main__":
    main()
