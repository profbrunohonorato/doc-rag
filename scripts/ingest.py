"""Indexa uma pasta sem iniciar o servidor HTTP."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from Presentation.API.settings import get_settings
from Infra.IoC.dependencies_helper import get_services


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    if not args.directory.is_dir():
        parser.error('Informe uma pasta existente')
    get_settings().documents_path = args.directory.resolve()
    services = get_services()
    services.db.initialize()
    try:
        documents = services.ingestion.scan()
        print(json.dumps(documents, default=str, ensure_ascii=False, indent=2))
        return int(any(d['status'] == 'error' for d in documents))
    finally:
        services.ai.close()
        services.db.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
