"""
main.py — CLI entry point. Orchestrates the pipeline:
  ingest → context → prompts → ai_client → validate → output
Run with --mock to verify wiring without an API key.
"""
import argparse
import logging
import sys

from dotenv import load_dotenv
load_dotenv()

from ingest import load_input
from context import load_backlog_context
from prompts import build_messages
from ai_client import generate
from validate import validate_and_repair
from output import write_output, print_summary

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser(description="Smart Backlog Assistant — convert notes into user stories.")
    p.add_argument("--input",   required=True, help=".txt, .md, or .pdf input file")
    p.add_argument("--backlog", default=None,  help="Existing backlog.json for deduplication (optional)")
    p.add_argument("--output",  default="output.json", help="Output file (default: output.json)")
    p.add_argument("--model",   default=None,  help="Model name override (overrides MODEL_NAME env var)")
    p.add_argument("--mock",    action="store_true", help="Return sample output without calling the API")
    return p.parse_args()


def main():
    args = parse_args()

    log.info("Input loaded: %s", args.input)
    # In mock mode, skip ingestion — generate() returns fixed sample data anyway
    input_text = "[mock]" if args.mock else load_input(args.input)

    backlog_context = ""
    if not args.mock and args.backlog:
        backlog_context = load_backlog_context(args.backlog)
        log.info("Backlog context loaded: %s", args.backlog)

    messages = [] if args.mock else build_messages(input_text, backlog_context)
    log.info("Prompt built (%d message(s))", len(messages))

    log.info("Request sent%s", " [MOCK]" if args.mock else "")
    raw = generate(messages, model_override=args.model, mock=args.mock)
    log.info("Response received")

    result = validate_and_repair(raw, messages, mock=args.mock)

    write_output(result, args.output)
    log.info("Output written: %s", args.output)
    print_summary(result)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as exc:
        log.error("Fatal: %s", exc)
        sys.exit(1)
