import ssl
import tempfile

__all__ = []

__CERT_DATA = """
-----BEGIN CERTIFICATE-----
MIICuDCCAmqgAwIBAgIURKmZE5o9LPqEQpU6yahiP+TLwpAwBQYDK2VwMIHHMQsw
CQYDVQQGEwJVUzETMBEGA1UECAwKQ2FsaWZvcm5pYTEWMBQGA1UEBwwNU2FuIEZy
YW5jaXNjbzEYMBYGA1UECgwPTWlzdGVyIFdlYmhvb2tzMRQwEgYDVQQLDAtFbmdp
bmVlcmluZzErMCkGA1UEAwwiS2Fma2EgQnJva2VyIENlcnRpZmljYXRlIEF1dGhv
cml0eTEuMCwGCSqGSIb3DQEJARYfZW5naW5lZXJpbmdAbWlzdGVyLXdlYmhvb2tz
LmNvbTAeFw0yNTA1MjIwNDA0NTZaFw0zNTA1MjAwNDA0NTZaMIHHMQswCQYDVQQG
EwJVUzETMBEGA1UECAwKQ2FsaWZvcm5pYTEWMBQGA1UEBwwNU2FuIEZyYW5jaXNj
bzEYMBYGA1UECgwPTWlzdGVyIFdlYmhvb2tzMRQwEgYDVQQLDAtFbmdpbmVlcmlu
ZzErMCkGA1UEAwwiS2Fma2EgQnJva2VyIENlcnRpZmljYXRlIEF1dGhvcml0eTEu
MCwGCSqGSIb3DQEJARYfZW5naW5lZXJpbmdAbWlzdGVyLXdlYmhvb2tzLmNvbTAq
MAUGAytlcAMhAE4/M7Qj1+KNtqGdGF7DgAtO+elzPGDHlyCLz1VCvwi+o2YwZDAd
BgNVHQ4EFgQUVVOr9w+0L3obSHwAx/3DKG+iKOMwHwYDVR0jBBgwFoAUVVOr9w+0
L3obSHwAx/3DKG+iKOMwEgYDVR0TAQH/BAgwBgEB/wIBATAOBgNVHQ8BAf8EBAMC
AQYwBQYDK2VwA0EAZlSOhxGZrIK/gUwB6tOKK3S0gvD7a+SoEEkAYVF44AnwvMe0
5qzICSe+0sFaqLT0CNf2JQo/PSK06e9Lb7zNCw==
-----END CERTIFICATE-----
"""


def new_ssl_client_context() -> ssl.SSLContext:
    cert_file = tempfile.NamedTemporaryFile()
    cert_file.write(
        bytes(__CERT_DATA, encoding="ascii"),
    )
    cert_file.flush()

    ctx: ssl.SSLContext = ssl.create_default_context()
    ctx.load_verify_locations(cafile=cert_file.name)
    cert_file.close()

    return ctx
