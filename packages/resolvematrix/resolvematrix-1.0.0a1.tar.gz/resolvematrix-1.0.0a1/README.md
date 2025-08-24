# ResolveMatrix

ResolveMatrix is a Python library providing the utilities required to resolve both client and server to server
API endpoints. It fully conforms to the Matrix specification outlined
[in the client-to-server specification](https://spec.matrix.org/v1.15/client-server-api/#server-discovery) and
[server-to-server specification](https://spec.matrix.org/v1.15/server-server-api/#server-discovery).

## Installing

For now, only available via Git:

```bash
pip install git+https://codeberg.org/timedout/resolvematrix.git
```

## Usage

### Command line

You can use the command `mxresolve` to resolve a server name from the command line:

```bash
$ mxresolve example.com
https://matrix.example.com
```

### Client to Server

You can resolve a server name as follows:

```python
import resolvematrix

resolver = resolvematrix.ClientResolver()
result = resolver.resolve("example.com")
print(result)  # "https://matrix.example.com"

# You can also use the server_from_user_id helper utility to extract the server name from a user ID:
result = resolver.resolve(resolvematrix.server_from_user_id("@alice:example.com"))
print(result)  # "https://matrix.example.com"

# And even manually pass a server URL!
result = resolver.resolve("https://matrix.example.com")
print(result)  # "https://matrix.example.com"
```

### Server to Server

You can resolve a server name as follows:

```python
import resolvematrix

resolver = resolvematrix.ServerResolver()
result = resolver.resolve("matrix.org")
print(repr(result))  # "ServerDestination(hostname='matrix-federation.matrix.org:443', host_header='matrix-federation.matrix.org:443', sni='matrix-federation.matrix.org')"

# You then need to do a little bit of wrangling to get an actual connection.
import httpx

response = resolver.client.get(
    f"{result.base_url}/_matrix/federation/v1/version",
    headers={"Host": result.host_header},
    extensions={"sni_hostname": result.sni} if result.sni else {},
).raise_for_status()

# Other libraries may have different ways of specifying SNI and custom Host headers.
# See also: https://stackoverflow.com/a/77743443
```

## Contact

Talk to me in my matrix room: [#ontopic:timedout.uk](https://matrix.to/#/#ontopic:timedout.uk).
