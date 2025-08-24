from ipaddress import (
    IPv4Address,
    IPv4Network,
    IPv6Address,
    IPv6Network,
)
from struct import unpack

from ..errors import PGCopyRecordError
from .nullables import if_nullable


IpAddr = {
    2: IPv4Address,
    3: IPv6Address,
}
IpNet = {
    IPv4Address: IPv4Network,
    IPv6Address: IPv6Network,
}


@if_nullable
def to_network(
    binary_data: bytes,
) -> IPv4Address|IPv6Address|IPv4Network|IPv6Network:
    """Unpack inet or cidr value."""

    ip_family, ip_netmask, is_cidr, ip_length, ip_data = unpack(
        f"!4B{len(binary_data) - 4}s",
        binary_data,
    )

    if ip_length != len(ip_data):
        raise PGCopyRecordError("Invalid IP data")

    ip_addr: IPv4Address|IPv6Address = IpAddr[ip_family](ip_data)

    if is_cidr:
        return IpNet[ip_addr.__class__](
            f"{ip_addr}/{ip_netmask}",
            strict=False,
        )

    return ip_addr
