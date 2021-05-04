# Copyright (C) 2021 Intel Corporation. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

import os
import logging

from extractors.helpers import get_node

PCI_IDS_PATHS = [
    "/usr/share/misc/pci.ids",
    "/usr/share/hwdata/pci.ids",
]

class PCI_IDs:
    def __init__(self, f):
        names = {}
        vendor_id = None
        device_id = None
        classes = {}
        class_id = None

        for line in f.readlines():
            line = line.strip("\n")
            if line == "" or line.startswith("#"):
                continue

            if line.startswith("\t\t"):
                if device_id is not None:
                    parts = line.strip().split("  ")
                    subvendor_id, subdevice_id = tuple(map(lambda x: int(x, base=16), parts[0].split(" ")))
                    desc = "  ".join(parts[1:])
                    names[(vendor_id, device_id, subvendor_id, subdevice_id)] = desc
            elif line.startswith("\t"):
                if vendor_id is not None:
                    parts = line.strip().split("  ")
                    device_id = int(parts[0], base=16)
                    desc = "  ".join(parts[1:])
                    names[(vendor_id, device_id)] = desc
                elif class_id is not None:
                    parts = line.strip().split("  ")
                    subclass_id = int(parts[0], base=16)
                    desc = "  ".join(parts[1:])
                    classes[(class_id, subclass_id)] = desc
            elif line.startswith("C"):
                parts = line.strip().split("  ")
                class_id = int(parts[0][2:], base=16)
                vendor_id = None
                device_id = None
                desc = "  ".join(parts[1:])
                classes[(class_id,)] = desc
            else:
                parts = line.strip().split("  ")
                vendor_id = int(parts[0], base=16)
                device_id = None
                class_id = None
                desc = "  ".join(parts[1:])
                names[(vendor_id,)] = desc

        self.__names = names
        self.__classes = classes

    def lookup(self, vendor_id, device_id, subsystem_vendor_id, subsystem_device_id, class_code):
        acc = []

        # Class
        if class_code:
            class_id = (class_code >> 16)
            subclass_id = ((class_code >> 8) & 0xFF)
            if (class_id, subclass_id) in self.__classes.keys():
                acc.append(self.__classes[(class_id, subclass_id)] + ":")
            elif (class_id,) in self.__classes.keys():
                acc.append(self.__classes[(class_id,)] + ":")

        # Vendor
        if vendor_id:
            if (vendor_id,) in self.__names.keys():
                acc.append(self.__names[(vendor_id,)])

        # Device
        if vendor_id and device_id:
            if (vendor_id, device_id) in self.__names.keys():
                acc.append(self.__names[(vendor_id, device_id)])

        return " ".join(acc)

def lookup_pci_device(element, ids):
    vendor_id = get_node(element, "vendor/text()")
    device_id = get_node(element, "identifier/text()")
    subsystem_vendor_id = get_node(element, "subsystem_vendor/text()")
    subsystem_device_id = get_node(element, "subsystem_identifier/text()")
    class_code = get_node(element, "class/text()")

    args = [vendor_id, device_id, subsystem_vendor_id, subsystem_device_id, class_code]
    desc = ids.lookup(*list(map(lambda x: int(x, base=16) if x else None, args)))

    if desc:
        element.set("description", desc)

def lookup_pci_devices(board_etree):
    # Lookup names of PCI devices from pci.ids if possible
    pci_id_path = None
    for path in PCI_IDS_PATHS:
        if os.path.exists(path):
            pci_id_path = path

    if pci_id_path:
        with open(pci_id_path, "r") as f:
            ids = PCI_IDs(f)

            devices = board_etree.xpath("//device")
            for device in devices:
                lookup_pci_device(device, ids)

            buses = board_etree.xpath("//bus")
            for bus in buses:
                lookup_pci_device(bus, ids)
    else:
        logging.info(f"Cannot find pci.ids under /usr/share. PCI device names will not be available.")

def extract(board_etree):
    lookup_pci_devices(board_etree)