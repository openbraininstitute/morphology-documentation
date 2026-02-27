from entitysdk.staging.circuit import stage_circuit
from pathlib import Path
import argparse
import logging
import os
import sys
from functools import partial

from entitysdk import Client, LocalAssetStore, ProjectContext, models
from entitysdk.token_manager import TokenFromFunction
from obi_auth import get_token

L = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

#virtual_lab_id = "84258ff5-114f-4865-9a2d-258575c23909"
#project_id = "c013bf9e-74e6-4486-bf06-5d414fc473c6"

def main():
    """Script to launch a task for a single configuration asset.

    Example usage.

    python launch_task_for_single_config_asset.py
        --entity_type Simulation
        --entity_id babb299c-782a-41f1-b782-bc4c5da45462

    Environment Variables Required:
        PERSISTENT_TOKEN_ID: Persistent authentication token.
        DEPLOYMENT: Deployment environment.
        LOCAL_STORE_PREFIX: Local asset store for file mounting.
    """
    for k, v in os.environ.items():
        print(f"{k}={v}")

    persistent_token_id = os.getenv("PERSISTENT_TOKEN_ID")
    deployment = os.getenv("DEPLOYMENT")
    local_store_prefix = os.getenv("LOCAL_STORE_PREFIX")

    print(f"{local_store_prefix}")

    if local_store_prefix:
        asdf = Path(local_store_prefix)
        print(list(asdf.glob('*')))


    try:
        parser = argparse.ArgumentParser(description="Test")

        parser.add_argument("--entity_type", required=True, help="EntitySDK entity type as string")
        parser.add_argument("--entity_id", required=True, help="Entity ID as string")
        parser.add_argument("--virtual_lab_id", required=True, help="Vlab id")
        parser.add_argument("--project_id", required=True, help="Vlab id")

        args = parser.parse_args()

    except ValueError as e:
        L.error(f"Argument parsing error: {e}")
        return 1

    token_manager = TokenFromFunction(
        partial(
            get_token,
            environment=deployment,
            auth_mode="persistent_token",
            persistent_token_id=persistent_token_id,
        ),
    )
    project_context = ProjectContext(
        project_id=project_id, virtual_lab_id=virtual_lab_id, environment=deployment
    )
    client = Client(
        environment=deployment,
        project_context=project_context,
        token_manager=token_manager,
        local_store=LocalAssetStore(prefix=local_store_prefix),
    )
    entity_type = getattr(models, args.entity_type)
    for entity_id in ("265213fd-98ae-4487-ba2a-f95f89bb51f4", #nbS1-HEX0_L4: aws_s3_internal
                      "1c81aa3e-7e9d-437a-91c8-aa5f7bc3bd02",): #nbS1-HEX0: aws_s3_open
        entity = client.get_entity(entity_type=entity_type, entity_id=entity_id)

        if args.entity_type == "Circuit":
            circuit_path = Path("/tmp/stage") / entity_id
            circuit_path.mkdir(parents=True, exist_ok=True)
            stage_circuit(
                client,
                model=entity,
                output_dir=circuit_path,
                max_concurrent=1,
            )

            print(list(circuit_path.glob('*')))

            count = 0
            for p in circuit_path.rglob('*'):
                if p.is_symlink():
                    print(p)
                    count += 1
                    if count > 100:
                        break


if __name__ == "__main__":
    sys.exit(main())
