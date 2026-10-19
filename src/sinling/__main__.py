"""Command line: ``python -m sinling <command>``."""

from __future__ import annotations

import argparse
import sys

from sinling.evaluation import TASKS, accuracy_table, evaluate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog='python -m sinling', description='Sinling, a Sinhala language toolkit.')
    commands = parser.add_subparsers(dest='command', required=True)
    ev = commands.add_parser('evaluate', help='score backends on test sets',
                             description='With no options, print the accuracy table for the default backends.')
    ev.add_argument('--task', choices=TASKS)
    ev.add_argument('--dataset', help='a registered dataset name or a CoNLL-U file')
    ev.add_argument('--backend', help="the backend to score (the task's default if omitted)")
    ev.add_argument('--text', choices=('detokenized', 'given'), default='detokenized')
    args = parser.parse_args(argv)

    if args.task is None and args.dataset is None:
        print(accuracy_table())
        return 0
    if args.task is None or args.dataset is None:
        parser.error('--task and --dataset go together')
    print(evaluate(args.task, args.dataset, args.backend, text=args.text))
    return 0


if __name__ == '__main__':
    sys.exit(main())
