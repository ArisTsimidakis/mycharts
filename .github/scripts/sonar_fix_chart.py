# Copyright 2024
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

""" Fixing Helm Chart based on Sonar results
"""

from typing import Callable
import re
import os
import copy
import json
import fix_template
import terrascan_fix_chart


def remove_duplicates(json_file: str) -> None:
    """Remove duplicate issues from the JSON file.

    Args:
        json_file (str): The path of the JSON file.
    """
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    seen_issues = set()
    unique_issues = []
    
    for issue in data.get("issues", []):
        identifier = (issue.get("rule"), issue.get("component"), issue.get("line"))
        
        if identifier not in seen_issues:
            seen_issues.add(identifier)
            unique_issues.append(issue)
    
    print(f"Unique issues: {unique_issues}")
    print(f"\nTotal number of unique issues: {len(unique_issues)}")
    data["issues"] = unique_issues
    data["total"] = len(unique_issues)
    
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)


def iterate_checks(chart_folder: str, json_path: str) -> None:
    """Parses JSON data and iterates "check_id" keys.

    Args:
        chart_folder (str): The name of the chart to fix.
        json_path (str): The path to the JSON file to parse.
    """

    # Remove duplicate issues
    remove_duplicates(json_path)

    # Load the JSON file
    with open(json_path, 'r', encoding="utf-8") as file:
        results = json.load(file)

    template = fix_template.parse_yaml_template(chart_folder)

    # List of all checks
    all_checks = []

    print("Starting to fix chart's issues ...\n")

    for issue in results["issues"]:
        print(f"{issue['rule']}: {issue['message']}")

        check_id = fix_issue(issue, template)

        all_checks.append(check_id)

    print("\nAll issues fixed!\n")

    # Print all found checks
    all_checks = [x for x in all_checks if x is not None]
    all_checks = ", ".join(all_checks)
    all_checks = all_checks.split(", ")
    all_checks.sort()
    print(f"Total number of checks: {len(all_checks)}")
    print(", ".join(all_checks))


    name = f"fixed_{chart_folder}_sonar_fixed"
    fix_template.save_yaml_template(template, name)


def fix_issue(issue, template: dict) -> str:
    """Fixes a check based on the Sonar check identifier.

    Args:
        issue (dict): The issue to fix.
        template (dict): The template to fix.
    """
    check_id = issue.get("rule")
    function = LookupClass.get_value(check_id)

    if function is None:
        print(f"No fix found for rule {check_id}")
        return None

    function = getattr(fix_template, function)
    return function(template, issue)


def fix_whitespace_issue(chart_folder:str, issue: dict) -> str:
    """Fixes the "Add a whitespace space before }} in the template directive" issue. 

    Args:
        chart_folder (str): The folder of the chart to fix.
        issue (dict): The issue to fix.
    """

    check_id = issue.get("rule")
    file_path = issue.get("component").split[':'][1]
    line_number = issue.get("line")
    start_offset = issue.get("textRange").get("startOffset")
    end_offset = issue.get("textRange").get("endOffset")

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        line = lines[line - 1]
        pre_fix = line[start_offset:end_offset]
        fixed_line = line[:start_offset] + " " + pre_fix.lstrip() + line[end_offset:]
        lines[line - 1] = fixed_line
        
        with open(file_path, 'w') as file:
            file.writelines(lines)

        print(f"Fixed whitespace issue in {file_path} at line {line_number}")
        return check_id
    except FileNotFoundError:
        print(f"File {file_path} not found")
    except IndexError:
        print(f"Index out of range for file {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")    

    return None

class LookupClass:
    """This class is used to lookup the function to be called for each rule.
    """

    _LOOKUP = {
        
    }

    @classmethod
    def get_value(cls, key) -> Callable:
        """ Get the function to be called for each check.

        Args:
            key (str): The check number.
        """
        return cls._LOOKUP.get(key)

    @classmethod
    def print_value(cls, key) -> None:
        """ Print the function to be called for each check."""
        print(cls._LOOKUP.get(key))

if __name__ == "__main__":
    remove_duplicates("sonar_result.json")