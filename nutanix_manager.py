"""
Nutanix Manager CLI - parity with vm_manager.py for Nutanix Prism v3
Capabilities:
- create: create VM from image (with one NIC)
- list: list VMs
- power: set power state (ON/OFF/RESET/SUSPEND)
- delete: delete VM

Configure using nutanix_config.json (see example below) or environment variables.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from typing import Any, Dict, Optional

from nutanix_client import NutanixClient


DEFAULT_CONFIG_PATH = os.path.join(os.getcwd(), "nutanix_config.json")


def load_config(path: str = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Nutanix config file not found: {path}. Create it based on nutanix_config.example.json"
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_client(cfg: Dict[str, Any]) -> NutanixClient:
    return NutanixClient(
        base_url=cfg["base_url"],
        username=cfg["username"],
        password=cfg["password"],
        verify_ssl=cfg.get("verify_ssl", True),
        project_uuid=cfg.get("project_uuid"),
    )


def cmd_list(args: argparse.Namespace, cfg: Dict[str, Any]) -> None:
    client = get_client(cfg)
    vms = client.list_vms(length=500)
    for vm in vms:
        spec = vm.get("spec", {})
        status = vm.get("status", {})
        name = spec.get("name")
        uuid = vm.get("metadata", {}).get("uuid")
        power = status.get("resources", {}).get("power_state")
        print(f"{name}\t{uuid}\t{power}")


def cmd_create(args: argparse.Namespace, cfg: Dict[str, Any]) -> None:
    client = get_client(cfg)
    name = args.name
    vcpus = args.cpu
    memory_mib = args.ram
    cluster_uuid = args.cluster_uuid
    subnet_uuid = args.subnet_uuid
    image_uuid = args.image_uuid
    boot_type = args.boot_type

    user_data_b64: Optional[str] = None
    if args.user_data and os.path.exists(args.user_data):
        with open(args.user_data, "r", encoding="utf-8") as f:
            user_data_b64 = client.b64_encode_text(f.read())

    res = client.create_vm(
        name=name,
        vcpus=vcpus,
        memory_mib=memory_mib,
        cluster_uuid=cluster_uuid,
        subnet_uuid=subnet_uuid,
        image_uuid=image_uuid,
        cores_per_vcpu=args.cores_per_vcpu,
        cloudinit_user_data_b64=user_data_b64,
        boot_type=boot_type,
    )
    print(json.dumps(res, indent=2))


def cmd_power(args: argparse.Namespace, cfg: Dict[str, Any]) -> None:
    client = get_client(cfg)
    res = client.set_power_state(args.uuid, args.state)
    print(json.dumps(res, indent=2))

    if args.wait:
        ok = client.wait_for_power_state(args.uuid, "ON" if args.state.upper() == "ON" else "OFF", timeout_s=600)
        print(f"wait result: {ok}")


def cmd_delete(args: argparse.Namespace, cfg: Dict[str, Any]) -> None:
    client = get_client(cfg)
    client.delete_vm(args.uuid)
    print("Deleted", args.uuid)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Nutanix Manager CLI")
    p.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to nutanix_config.json")
    sub = p.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List VMs")
    p_list.set_defaults(func=cmd_list)

    p_create = sub.add_parser("create", help="Create VM from image")
    p_create.add_argument("name")
    p_create.add_argument("--cpu", type=int, default=2)
    p_create.add_argument("--ram", type=int, default=4096, help="RAM in MiB")
    p_create.add_argument("--cluster-uuid", required=True)
    p_create.add_argument("--subnet-uuid", required=True)
    p_create.add_argument("--image-uuid", required=True)
    p_create.add_argument("--cores-per-vcpu", type=int, default=1)
    p_create.add_argument("--boot-type", default="UEFI", choices=["UEFI", "LEGACY"])
    p_create.add_argument("--user-data", help="Path to cloud-init user-data")
    p_create.set_defaults(func=cmd_create)

    p_power = sub.add_parser("power", help="Set power state")
    p_power.add_argument("uuid")
    p_power.add_argument("--state", required=True, choices=["ON", "OFF", "RESET", "SUSPEND"])
    p_power.add_argument("--wait", action="store_true", help="Wait for final state")
    p_power.set_defaults(func=cmd_power)

    p_delete = sub.add_parser("delete", help="Delete VM")
    p_delete.add_argument("uuid")
    p_delete.set_defaults(func=cmd_delete)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    args = build_parser().parse_args(argv)
    cfg = load_config(args.config)
    args.func(args, cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())