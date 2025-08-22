#!/usr/bin/env python3
"""
Registry cleanup CLI tool.
Combines functionality for deleting old image tags and listing repository catalogs.
"""

import argparse
import base64
import hashlib
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from uuid import uuid4

import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, load_pem_private_key
from requests import HTTPError

# Constants
MAX_TAGS_STORE = 3
TOKEN_VALID_FOR_SECONDS = 3600
ISSUER = "houston"


def setup_logging(debug=False):
    """Configure logging based on environment and debug flag."""
    log_level = logging.DEBUG if debug or os.environ.get("DEBUG") else logging.INFO
    logging.basicConfig(
        level=log_level,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def get_k8s_secret_key(namespace, secret_name):
    """Get private key from Kubernetes secret."""
    try:
        from kubernetes import client, config  # noqa: PLC0415

        try:
            config.load_incluster_config()
            logging.info("Using in-cluster kubernetes configuration")
        except config.ConfigException:
            config.load_kube_config()
            logging.info("Using kubectl kubernetes configuration")

        kube = client.CoreV1Api()
        secret = kube.read_namespaced_secret(secret_name, namespace)
        tls_private_key = secret.data.get("tls.key")
        if not tls_private_key:
            raise ValueError("tls.key not found in secret")
        return base64.b64decode(tls_private_key)
    except ImportError:
        raise ImportError("kubernetes package required for K8s secret access")


def get_local_private_key(key_path="./keys/tls.key"):
    """Get private key from local file."""
    try:
        with open(key_path, "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Private key file not found: {key_path}")


def get_kid(private_key_data):
    """Generate key ID from private key."""
    pem_private_key = load_pem_private_key(private_key_data, password=None, backend=default_backend())
    public_key = pem_private_key.public_key()
    der_public_key = public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    sha256 = hashlib.sha256(der_public_key)
    base32_payload = base64.b32encode(sha256.digest()[:30]).decode("utf-8")
    return ":".join([base32_payload[i : i + 4] for i in range(0, 48, 4)])


def get_private_key_object(private_key_data):
    """Convert private key data to cryptography object."""
    return serialization.load_pem_private_key(private_key_data, password=None, backend=default_backend())


def create_jwt_token(private_key_data, client=None):
    """Create JWT token for registry access."""
    now = datetime.now(datetime.UTC)

    access_permissions = [{"type": "registry", "name": "catalog", "actions": ["*"]}]
    if client:
        access_permissions.append({"type": "repository", "name": f"{client}/airflow", "actions": ["pull", "*"]})

    payload = {
        "iss": ISSUER,
        "sub": "registry",
        "aud": "docker-registry",
        "exp": now + timedelta(seconds=TOKEN_VALID_FOR_SECONDS),
        "nbf": now,
        "iat": now,
        "jti": uuid4().hex,
        "access": access_permissions,
    }

    private_key = get_private_key_object(private_key_data)
    return jwt.encode(payload, private_key, headers={"kid": get_kid(private_key_data)}, algorithm="RS256")


def create_session(token):
    """Create requests session with authentication."""
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}", "Accept": "application/vnd.docker.distribution.manifest.v2+json"})
    return session


def list_repositories(session, registry):
    """List all repositories in the registry catalog."""
    logging.info("Fetching repositories from registry catalog")

    try:
        response = session.get(f"https://{registry}/v2/_catalog", timeout=600)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to connect to registry: {e}")
        return []

    data = response.json()
    repositories = data.get("repositories", [])

    if repositories:
        logging.info(f"Found {len(repositories)} repositories")
        logging.info(f"Request took {response.elapsed.total_seconds():.2f} seconds")
    else:
        logging.warning("No repositories found")

    return repositories


def get_image_tags(session, registry, client):
    """Get all tags for a specific client's airflow repository."""
    try:
        response = session.get(f"https://{registry}/v2/{client}/airflow/tags/list")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get tags for {client}: {e}")
        return []

    data = response.json()
    tags = data.get("tags", [])

    if not tags:
        logging.warning(f"No tags found for {client}/airflow")
        return []

    # Filter for CLI tags with pattern: prefix-number
    cli_tags = [tag for tag in tags if re.match(r".*-\d+$", tag)]
    return sorted(cli_tags, key=lambda x: int(x.split("-")[-1]))


def keep_latest_tag(tags, prefix):
    """Remove the latest tag with given prefix from deletion list."""
    if not tags:
        return tags

    prefix_tags = [tag for tag in tags if tag.startswith(f"{prefix}-")]
    if not prefix_tags:
        return tags

    latest_tag = max(prefix_tags, key=lambda tag: int(tag.split("-")[-1]))
    logging.info(f"Preserving latest {prefix} tag: {latest_tag}")
    return [tag for tag in tags if tag != latest_tag]


def get_manifest_digest(session, registry, client, tag):
    """Get manifest digest for a specific tag."""
    response = session.get(f"https://{registry}/v2/{client}/airflow/manifests/{tag}")
    response.raise_for_status()
    return response.headers["Docker-Content-Digest"]


def delete_manifest(session, registry, client, digest):
    """Delete a manifest by digest."""
    response = session.delete(f"https://{registry}/v2/{client}/airflow/manifests/{digest}")
    response.raise_for_status()


def cmd_list_repos(args):
    """List repositories command."""
    setup_logging(args.debug)

    if args.k8s_secret:
        if not args.namespace:
            logging.error("--namespace required when using --k8s-secret")
            return 1
        private_key_data = get_k8s_secret_key(args.namespace, args.k8s_secret)
    else:
        private_key_data = get_local_private_key(args.key_path)

    token = create_jwt_token(private_key_data)
    session = create_session(token)

    repositories = list_repositories(session, args.registry)

    if args.clients_only:
        # Extract client names (remove /airflow suffix)
        clients = sorted({repo.split("/")[0] for repo in repositories if "/airflow" in repo})
        print("\n".join(clients))
    else:
        print("\n".join(repositories))

    return 0


def cmd_delete_tags(args):
    """Delete old image tags command."""
    setup_logging(args.debug)

    if args.k8s_secret:
        if not args.namespace:
            logging.error("--namespace required when using --k8s-secret")
            return 1
        private_key_data = get_k8s_secret_key(args.namespace, args.k8s_secret)
    else:
        private_key_data = get_local_private_key(args.key_path)

    token = create_jwt_token(private_key_data, args.client)
    session = create_session(token)

    tags = get_image_tags(session, args.registry, args.client)
    if not tags:
        logging.info("No tags found to process")
        return 0

    # Keep the latest tag with the specified prefix
    tags = keep_latest_tag(tags, args.prefix)

    # Calculate which tags to delete (keep MAX_TAGS_STORE newest)
    if len(tags) <= MAX_TAGS_STORE:
        logging.info(f"Only {len(tags)} tags found, need more than {MAX_TAGS_STORE} to delete any")
        return 0

    tags_to_delete = tags[:-MAX_TAGS_STORE]
    logging.info(f"Will delete {len(tags_to_delete)} tags: {tags_to_delete}")

    if args.dry_run:
        logging.info("Dry run - no tags will be deleted")
        return 0

    deleted_count = 0
    for tag in tags_to_delete:
        try:
            digest = get_manifest_digest(session, args.registry, args.client, tag)
            delete_manifest(session, args.registry, args.client, digest)
            logging.info(f"Deleted tag: {tag}")
            deleted_count += 1
        except HTTPError as e:
            logging.error(f"Failed to delete tag {tag}: {e}")

    logging.info(f"Successfully deleted {deleted_count}/{len(tags_to_delete)} tags")
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Docker registry cleanup tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global options
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("-r", "--registry", required=True, help="Registry host (e.g., registry.example.com)")

    # Authentication options
    auth_group = parser.add_mutually_exclusive_group()
    auth_group.add_argument("--k8s-secret", help="Get private key from Kubernetes secret")
    auth_group.add_argument("--key-path", default="./keys/tls.key", help="Path to private key file (default: ./keys/tls.key)")

    parser.add_argument("-n", "--namespace", help="Kubernetes namespace (required with --k8s-secret)")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List repositories command
    list_parser = subparsers.add_parser("list-repos", help="List repository catalog")
    list_parser.add_argument("--clients-only", action="store_true", help="Show only client names (strip /airflow suffix)")
    list_parser.set_defaults(func=cmd_list_repos)

    # Delete tags command
    delete_parser = subparsers.add_parser("delete-tags", help="Delete old image tags")
    delete_parser.add_argument("client", help="Airflow deployment release name")
    delete_parser.add_argument("-p", "--prefix", required=True, help="Tag prefix pattern (e.g., deploy, cli)")
    delete_parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without deleting")
    delete_parser.set_defaults(func=cmd_delete_tags)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        return args.func(args)
    except KeyboardInterrupt:
        logging.info("Operation cancelled by user")
        return 1
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        if args.debug:
            raise
        return 1


if __name__ == "__main__":
    sys.exit(main())
