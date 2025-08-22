#!/usr/bin/env python3

import json
import logging
import os
import pathlib
import sys
from itertools import zip_longest
from typing import Iterator, Optional

import click
import grpc
import numpy as np
import phonexia.grpc.common.core_pb2 as phx_common
import phonexia.grpc.technologies.speaker_identification.v1.speaker_identification_pb2 as sid
import phonexia.grpc.technologies.speaker_identification.v1.speaker_identification_pb2_grpc as sid_grpc

MAX_BATCH_SIZE = 1024


def list_reader(list_path) -> Iterator[str]:
    logging.info(f"Opening file; {list_path}")
    with open(list_path) as file:
        for vp_path in file.read().splitlines():
            if os.path.exists(vp_path):
                yield vp_path


def parse_vp(path: str) -> phx_common.Voiceprint:
    logging.info(f"Opening voiceprint: {path}")
    with open(path, mode="rb") as file:
        return phx_common.Voiceprint(content=file.read())


def make_compare_request(list_a: Iterator[str], list_b: Iterator[str]) -> Iterator[sid.CompareRequest]:
    batch_size = 0
    request = sid.CompareRequest()

    for file_a, file_b in zip_longest(list_a, list_b):
        if batch_size >= MAX_BATCH_SIZE:
            yield request
            batch_size = 0
            request = sid.CompareRequest()

        if file_a:
            vp = parse_vp(file_a)
            request.voiceprints_a.append(vp)
            batch_size += 1

        if file_b:
            vp = parse_vp(file_b)
            request.voiceprints_b.append(vp)
            batch_size += 1

    # Yield the last request if it contains any voiceprints
    if len(request.voiceprints_a) or len(request.voiceprints_b):
        yield request


def print_scores(rows: int, cols: int, result: list, to_json: bool = False) -> None:
    mat = np.array(result).reshape(rows, cols)
    if to_json:
        score = {"score": mat.tolist()}
        print(json.dumps(score, indent=2))
    else:
        print("Score:")
        for row in mat:
            for val in row:
                print(f"{val:7.1f}", end=" ")
            print("")


def compare_one_to_one(
        file1: str, file2: str, channel: grpc.Channel, metadata: Optional[list], to_json: bool = False
) -> None:
    stub = stub = sid_grpc.VoiceprintComparisonStub(channel)
    result = stub.Compare(make_compare_request(iter([file1]), iter([file2])), metadata=metadata)
    for res in result:
        print_scores(1, 1, [res.scores.values], to_json)


def compare_m_to_n(
        list1: Iterator[str],
        list2: Iterator[str],
        channel: grpc.Channel,
        metadata: Optional[list],
        to_json: bool = False,
) -> None:
    stub = sid_grpc.VoiceprintComparisonStub(channel)
    n_rows = 0
    n_cols = 0
    scores = []
    requests = make_compare_request(list1, list2)
    for result in stub.Compare(requests, metadata=metadata):
        if result.scores.rows_count:
            n_rows = result.scores.rows_count
            n_cols = result.scores.columns_count
        scores.extend(result.scores.values)

    print_scores(n_rows, n_cols, scores, to_json)


def merge_voiceprints(files: list[pathlib.Path], channel: grpc.Channel, metadata: Optional[list] = None,
                      output: Optional[pathlib.Path] = None):
    stub = sid_grpc.VoiceprintMergingStub(channel)
    request = sid.MergeRequest(voiceprints=[parse_vp(f) for f in files])
    result = stub.Merge(request, metadata=metadata)
    if output:
        with open(output, mode="wb") as file:
            file.write(result.voiceprint.content)
            logging.info(f"Saved merged voiceprint to {output}")
    else:
        sys.stdout.buffer.write(result.voiceprint.content)


pass_ctx = click.make_pass_decorator(dict, ensure=True)


@click.group(context_settings={'show_default': True, "help_option_names":['-h', '--help']})
@click.option("--host", "-H", default="localhost:8080", help="Server address")
@click.option("--log-level", "-l", type=click.Choice(["critical", "error", "warning", "info", "debug"]),
              default="error", help="Logging level")
@click.option("--metadata", metavar="key=value", multiple=True, type=lambda x: tuple(x.split("=")),
              help="Custom client metadata")
@click.option("--plaintext", is_flag=True, help="Use insecure plaintext connection")
@pass_ctx
def cli(ctx, host, log_level, metadata, plaintext):
    """Voiceprint Comparison gRPC client. Compares voiceprints and returns scores."""
    ctx["host"] = host
    ctx["metadata"] = metadata
    ctx["plaintext"] = plaintext

    logging.basicConfig(
        level=log_level.upper(),
        format="[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@cli.command()
@click.option("--files", nargs=2, type=click.Path(exists=True),
              help="Files for 1x1 comparison, requires exactly two arguments", required=False)
@click.option("--lists", nargs=2, type=click.Path(exists=True),
              help="Lists of files for MxN comparison (text file with one path to a voiceprint per line), requires exactly two arguments",
              required=False)
@click.option("--to-json", is_flag=True, help="Output comparison to json")
@pass_ctx
def compare(ctx, files, lists, to_json):
    """Compare voiceprints"""

    host = ctx["host"]
    metadata = ctx["metadata"]
    plaintext = ctx["plaintext"]
    # Ensure exactly one of files or lists is provided (mutually exclusive)
    if files and lists:
        raise click.ClickException("Cannot use both --files and --lists options together")
    if not files and not lists:
        raise click.ClickException("Must provide either --files or --lists option")

    try:
        logging.info(f"Connecting to {host}")
        channel = (
            grpc.insecure_channel(target=host)
            if plaintext
            else grpc.secure_channel(target=host, credentials=grpc.ssl_channel_credentials())
        )
        if files:
            compare_one_to_one(
                files[0], files[1], channel, metadata, to_json
            )
        elif lists:
            compare_m_to_n(
                list_reader(lists[0]),
                list_reader(lists[1]),
                channel,
                metadata,
                to_json,
            )
    except grpc.RpcError:
        logging.exception("RPC failed")
        exit(1)
    except Exception:
        logging.exception("Unknown error")
        exit(1)


@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Save merged voiceprint to output file")
@pass_ctx
def merge(ctx, files, output):
    """Merge voiceprints. Result voiceprint is written to stdout by default."""
    host = ctx["host"]
    metadata = ctx["metadata"]
    plaintext = ctx["plaintext"]
    try:
        logging.info(f"Connecting to {host}")
        channel = (
            grpc.insecure_channel(target=host)
            if plaintext
            else grpc.secure_channel(target=host, credentials=grpc.ssl_channel_credentials())
        )
        merge_voiceprints(files, channel, metadata, output)
    except grpc.RpcError:
        logging.exception("RPC failed")
        exit(1)
    except Exception:
        logging.exception("Unknown error")
        exit(1)


if __name__ == "__main__":
    cli()