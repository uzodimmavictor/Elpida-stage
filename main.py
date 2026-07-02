import argparse
import os
import sys

import context


def main():
    # if len(sys.arg) #plus petit que 2
    configFile = sys.argv[1]
    context = Context()
    context.readConfigFile()

    parser = argparse.ArgumentParser(description="IA-Agent Elpida")

    parser.add_argument(
        "action",
        choices=["run", "stop"],
        help="The action to perform on the service (run or stop)",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="config.json",
        help="Path to the configuration JSON file (default: config.json)",
    )
