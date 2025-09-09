"""
Nutanix Prism v3 API client (minimal) for VM lifecycle operations.
- Auth: Basic auth against Prism Central/Element
- Endpoints: /api/nutanix/v3/*

NOTE: Adjust base_url to your Prism URL, and ensure the account has API permissions.
"""
from __future__ import annotations
import base64
import json
import time
from typing import Any, Dict, List, Optional

import requests


class NutanixClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        verify_ssl: bool = True,
        project_uuid: Optional[str] = None,
        timeout: int = 60,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        auth_str = f"{username}:{password}".encode()
        self.session.headers["Authorization"] = "Basic " + base64.b64encode(auth_str).decode()
        self.project_uuid = project_uuid
        self.timeout = timeout

    # ---------- Low-level helpers ----------
    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _get(self, path: str) -> Dict[str, Any]:
        resp = self.session.get(self._url(path), timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = self.session.post(self._url(path), data=json.dumps(payload), timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def _delete(self, path: str) -> None:
        resp = self.session.delete(self._url(path), timeout=self.timeout)
        resp.raise_for_status()

    # ---------- Discovery ----------
    def list_vms(self, length: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        body = {"kind": "vm", "length": length, "offset": offset}
        res = self._post("/api/nutanix/v3/vms/list", body)
        return res.get("entities", [])

    def list_images(self, length: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        body = {"kind": "image", "length": length, "offset": offset}
        res = self._post("/api/nutanix/v3/images/list", body)
        return res.get("entities", [])

    def list_subnets(self, length: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        body = {"kind": "subnet", "length": length, "offset": offset}
        res = self._post("/api/nutanix/v3/subnets/list", body)
        return res.get("entities", [])

    def list_clusters(self, length: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        body = {"kind": "cluster", "length": length, "offset": offset}
        res = self._post("/api/nutanix/v3/clusters/list", body)
        return res.get("entities", [])

    def get_vm_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        # Simple scan; for production, use proper filtering if available
        vms = self.list_vms(length=500)
        for vm in vms:
            if vm.get("spec", {}).get("name") == name:
                return vm
        return None

    def get_vm(self, uuid: str) -> Dict[str, Any]:
        return self._get(f"/api/nutanix/v3/vms/{uuid}")

    # ---------- VM lifecycle ----------
    def create_vm(
        self,
        name: str,
        vcpus: int,
        memory_mib: int,
        cluster_uuid: str,
        subnet_uuid: str,
        image_uuid: str,
        cores_per_vcpu: int = 1,
        cloudinit_user_data_b64: Optional[str] = None,
        boot_type: str = "UEFI",
    ) -> Dict[str, Any]:
        """
        Create a VM from an image with one NIC.
        memory_mib: RAM in MiB
        vcpus: total vCPUs (sockets = vcpus, num_vcpus_per_socket = cores_per_vcpu)
        """
        vm_spec: Dict[str, Any] = {
            "spec": {
                "name": name,
                "resources": {
                    "num_vcpus_per_socket": max(1, int(cores_per_vcpu)),
                    "num_sockets": max(1, int(vcpus)),
                    "memory_size_mib": max(512, int(memory_mib)),
                    "boot_config": {
                        "boot_type": boot_type,
                    },
                    "cluster_reference": {
                        "kind": "cluster",
                        "uuid": cluster_uuid,
                    },
                    "disk_list": [
                        {
                            "data_source_reference": {
                                "kind": "image",
                                "uuid": image_uuid,
                            }
                        }
                    ],
                    "nic_list": [
                        {
                            "subnet_reference": {
                                "kind": "subnet",
                                "uuid": subnet_uuid,
                            }
                        }
                    ],
                },
            },
            "metadata": {"kind": "vm"},
        }
        if self.project_uuid:
            vm_spec["metadata"]["project_reference"] = {
                "kind": "project",
                "uuid": self.project_uuid,
            }
        if cloudinit_user_data_b64:
            vm_spec["spec"]["resources"]["guest_customization"] = {
                "cloud_init": {
                    "user_data": cloudinit_user_data_b64
                }
            }
        res = self._post("/api/nutanix/v3/vms", vm_spec)
        return res

    def set_power_state(self, vm_uuid: str, state: str = "ON") -> Dict[str, Any]:
        state = state.upper()
        if state not in {"ON", "OFF", "RESET", "SUSPEND"}:
            raise ValueError("Invalid power state. Use ON|OFF|RESET|SUSPEND")
        body = {"transition": state}
        return self._post(f"/api/nutanix/v3/vms/{vm_uuid}/set_power_state", body)

    def delete_vm(self, vm_uuid: str) -> None:
        self._delete(f"/api/nutanix/v3/vms/{vm_uuid}")

    # ---------- Utilities ----------
    @staticmethod
    def b64_encode_text(text: str) -> str:
        return base64.b64encode(text.encode()).decode()

    def wait_for_power_state(self, vm_uuid: str, desired: str, timeout_s: int = 600, poll_s: int = 5) -> bool:
        desired = desired.upper()
        end = time.time() + timeout_s
        while time.time() < end:
            vm = self.get_vm(vm_uuid)
            power_state = (
                vm.get("status", {})
                .get("resources", {})
                .get("power_state")
            )
            if power_state == desired:
                return True
            time.sleep(poll_s)
        return False