#!/usr/bin/env python
import argparse
import os
from time import sleep
from typing import List, Optional
from urllib.parse import urljoin

import requests

# Constants
DEFAULT_DIR_DEPTH = 7
MAX_SECONDS_PER_JOB = 120
SECONDS_BETWEEN_POLL = 1


def log(message: str = "", *args, **kwargs):
    if not message:
        print()
    print(message, *args, **kwargs)


def get_api_token(api_token: Optional[str] = None) -> Optional[str]:
    """Returns the API-token from environment variable"""
    if api_token:
        return api_token
    api_token = os.getenv("POFILE_API_KEY")
    return api_token


def get_default_dir_depth() -> Optional[int]:
    default_dir_depth = os.getenv("POFILE_DEFAULT_DIR_DEPTH", DEFAULT_DIR_DEPTH)
    return default_dir_depth


def get_api_domain_url() -> str:
    """Returns the API-domain URL, usually 'https://pofile.io'"""
    DEFAULT_POFILE_API_DOMAIN_URL = "https://pofile.io"
    api_domain_url = os.getenv("POFILE_API_DOMAIN_URL", DEFAULT_POFILE_API_DOMAIN_URL)
    return api_domain_url


def get_api_url_for_download_endpoint(job_id) -> str:
    """Returns the URL to the download API-endpoint of the given job"""
    api_domain_url = get_api_domain_url()
    endpoint_url = urljoin(api_domain_url, f"/api/download/{job_id}/")
    return endpoint_url


def get_api_url_for_upload_endpoint() -> str:
    """Returns the URL to the upload API-endpoint"""
    api_domain_url = get_api_domain_url()
    endpoint_url = urljoin(api_domain_url, "/api/upload/")
    return endpoint_url


def find_po_files(directory, dir_depth=5) -> List[str]:
    relative_paths = []
    base_depth = str(directory).rstrip(os.sep).count(os.sep)

    for root, _, files in os.walk(directory):
        current_depth = root.count(os.sep) - base_depth
        if current_depth > dir_depth:
            continue

        for file in files:
            if file.endswith(".po"):
                relative_path = os.path.relpath(os.path.join(root, file), directory)

                relative_paths.append(relative_path)
    return relative_paths


def is_valid_po_content(content: str) -> bool:
    """Returns True if the provided content is likely from an actual PO file"""
    if '"Language: ' not in content:
        # Require the Language-meta
        return False
    if 'msgid "' not in content:
        # Require at least one msgid
        return False
    if 'msgstr "' not in content:
        # Require at least one msgstr
        return False
    return True


def is_probably_po_file(relative_path: str) -> bool:
    """Return True if the file is probably an actual PO file"""
    with open(relative_path, "r") as file:
        content = file.read()
    is_valid = is_valid_po_content(content)
    return is_valid


def send_to_pofile_service(
    relative_path: str, api_token: Optional[str] = None
) -> Optional[str]:
    """Given a relative path, loads the PO file at the location and sends the content to the service"""
    api_url_for_upload = get_api_url_for_upload_endpoint()

    with open(relative_path, "rb") as file:
        files = {"po_file": file}

        headers = dict()
        if api_token:
            headers["Authorization"] = f"Bearer {api_token}"

        response = requests.post(
            api_url_for_upload,
            files=files,
            headers=headers,
        )

    # Check if the request was successful
    if response.status_code == 200:
        # log("OK: File sent successfully:", response.json())
        job_id = response.json()["job_id"]
    else:
        log(
            f"ERROR: Failed to send file for processing: {response.status_code} {response.text}",
        )
        return None

    return job_id


def main():
    parser = argparse.ArgumentParser(description="Manage PO files.")

    default_dir_depth = get_default_dir_depth()

    # Populate subcommand
    subparsers = parser.add_subparsers(dest="command")
    populate_parser = subparsers.add_parser(
        "populate", help="Populate all PO files in the project."
    )
    populate_parser.add_argument(
        "-y", "--yes", action="store_true", help="Skip confirmation prompt"
    )
    populate_parser.add_argument(
        "dir",
        type=str,
        nargs="?",
        default=".",
        help="Directory to search for PO files. Default is the current directory.",
    )
    populate_parser.add_argument(
        "--api-key",
        type=str,
        help="The API key of your account at pofile.io.",
    )
    populate_parser.add_argument(
        "--dir-depth",
        type=int,
        default=default_dir_depth,
        help=f"Maximum directory depth to search. Default is {default_dir_depth}.",
    )

    args = parser.parse_args()
    command = args.command

    if command == "populate":
        directory_path = args.dir
        dir_depth = args.dir_depth
        api_token_from_args = args.api_key
        api_token = get_api_token(api_token_from_args)

        # Populate PO files
        log(
            f"Looking for PO files at {directory_path if directory_path != '.' else 'the current directory'}"
        )
        relative_paths = find_po_files(directory_path, dir_depth)
        if not relative_paths:
            log(f"No PO files were found within the directory tree: {directory_path}")
            return
        log(f"Found {len(relative_paths)} PO file(s):")
        for path in relative_paths:
            log(f"  - {path}")
        if not args.yes:
            prompt = input(
                "Press 'y' to update the PO files with missing translations, or any other key to abort: "
            )
            if prompt.lower() != "y":
                log("Aborted by user.")
                return

        # Send each file to API
        pofile_abs_path_by_job_id = dict()
        for relative_path in relative_paths:
            abs_path = os.path.join(directory_path, relative_path)
            if not is_probably_po_file(abs_path):
                log(
                    f"Skipping {relative_path}: File does not appear to be a valid PO file"
                )
                continue
            job_id = send_to_pofile_service(abs_path, api_token=api_token)
            if job_id:
                pofile_abs_path_by_job_id[job_id] = abs_path

        job_ids = pofile_abs_path_by_job_id.keys()

        if not job_ids:
            log("No action: No PO files to populate.")
            return

        # Wait for each task to finish
        log(f"Waiting for {len(job_ids)} PO file(s) to be processed...")
        for job_id in job_ids:
            download_url = get_api_url_for_download_endpoint(job_id)
            # Poll job until available, and write result to the local PO file
            for _ in range(MAX_SECONDS_PER_JOB):
                response = requests.get(download_url)
                can_file_be_downloaded = response.status_code == 200
                if can_file_be_downloaded:
                    content = response.content
                    relative_path = pofile_abs_path_by_job_id[job_id]
                    with open(relative_path, "wb") as downloaded_file:
                        downloaded_file.write(content)
                    # Done with this file, so break the current loop
                    log()
                    break
                sleep(SECONDS_BETWEEN_POLL)
                log(".", end="", flush=True)
        log(f"OK: {relative_path} (modified)")
        log("Done.")


if __name__ == "__main__":
    main()
