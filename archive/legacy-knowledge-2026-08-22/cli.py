import argparse
import sys
from pathlib import Path
import json

def list_sources():
    registry_dir = Path(__file__).parent / "source-registry"
    if not registry_dir.exists():
        print("Registry directory not found.")
        return
    
    json_files = list(registry_dir.glob("*.json"))
    if not json_files:
        print("No sources found.")
        return
        
    print(f"Found {len(json_files)} sources:")
    for f in json_files:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"- {data.get('source_id')}: {data.get('name')} ({data.get('type')})")

def update_source(source_id: str):
    print(f"Updating source: {source_id} (mock)")

def update_all_sources():
    print("Updating all sources (mock)")

def search_knowledge(query: str):
    print(f"Searching for: {query} (mock)")

def main():
    parser = argparse.ArgumentParser(description="Knowledge Base CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list-sources
    list_parser = subparsers.add_parser("list-sources", help="List all registered sources")

    # update
    update_parser = subparsers.add_parser("update", help="Update a specific source")
    update_parser.add_argument("source_id", type=str, help="ID of the source to update")

    # update-all
    update_all_parser = subparsers.add_parser("update-all", help="Update all registered sources")

    # search
    search_parser = subparsers.add_parser("search", help="Search the knowledge base")
    search_parser.add_argument("query", type=str, help="Search query")

    args = parser.parse_args()

    if args.command == "list-sources":
        list_sources()
    elif args.command == "update":
        update_source(args.source_id)
    elif args.command == "update-all":
        update_all_sources()
    elif args.command == "search":
        search_knowledge(args.query)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
