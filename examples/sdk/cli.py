from __future__ import annotations

import argparse
import os

from amesh_client.execution import ExecutionClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("namespace")
    parser.add_argument("flow_id")
    parser.add_argument("--name", default="SDK CLI")
    args = parser.parse_args()
    client = ExecutionClient(
        os.environ["AMESH_ENDPOINT"],
        os.environ["AMESH_TOKEN"],
        os.getenv("AMESH_TENANT", "default"),
    )
    launched = client.launch(args.namespace, args.flow_id, inputs={"name": args.name})
    completed = client.wait(str(launched.execution.execution_id))
    print(completed.execution.state.value)


if __name__ == "__main__":
    main()
