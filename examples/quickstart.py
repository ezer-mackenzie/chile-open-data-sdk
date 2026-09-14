"""Print titles from one typed catalog search (contacts the live public portal)."""

from chile_open_data_sdk import ChileOpenDataClient


def main() -> None:
    """Search one page and close the shared connection pool."""
    with ChileOpenDataClient() as client:
        result = client.datasets.search("transport", rows=5)
        for dataset in result.results:
            print(dataset.title)


if __name__ == "__main__":
    main()
