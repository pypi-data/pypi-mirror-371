import argparse
import logging

from .client import ClientResolver
from .server import ServerResolver


def main():
    parser = argparse.ArgumentParser(description="Resolve a matrix server name")
    parser.add_argument("server_name", type=str, help="The matrix server name to resolve")
    args = parser.parse_args()

    cr = ClientResolver()
    sr = ServerResolver()
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("resolvematrix").setLevel(logging.DEBUG)
    print("Client resolution:", cr.resolve(args.server_name))
    print("Server resolution:", sr.resolve(args.server_name))
