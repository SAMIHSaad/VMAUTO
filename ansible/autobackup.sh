#!/bin/bash
# This script is run by systemd on shutdown to trigger a host-side snapshot.

# Path to VMware Tools daemon command-line interface
VMTOOLSD_CMD="/usr/bin/vmtoolsd"

# Get the VM's name from guestinfo variable set by Packer
VM_NAME=$($VMTOOLSD_CMD --cmd "info-get guestinfo.vm.name")

if [ -z "$VM_NAME" ]; then
    # If guestinfo fails, exit gracefully. Log this to syslog.
    logger "AUTOBACKUP: Could not get VM name from guestinfo. Snapshot skipped."
    exit 0
fi

# Log the attempt to syslog
logger "AUTOBACKUP: Requesting snapshot for VM: $VM_NAME"

# Execute the 'snapshot' script alias on the host, passing the VM name as an argument.
# The alias is configured in the .vmx file by Packer.
$VMTOOLSD_CMD --cmd "guest.run.script script='snapshot' args='$VM_NAME'"

# Give the host a moment to start the snapshot process before the guest powers off.
# This is a small delay to improve reliability.
sleep 3

logger "AUTOBACKUP: Snapshot request sent to host."

exit 0
