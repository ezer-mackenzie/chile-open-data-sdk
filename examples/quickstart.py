"""Search a small page of public dataset metadata."""

from chile_open_data import ChileOpenDataClient


def main() -> None:
    """Print titles from the first five matching datasets."""
    with ChileOpenDataClient() as client:
        result = client.actions.call("package_search", {"q": "transport", "rows": 5})
        datasets = result.get("results") if isinstance(result, dict) else None
        if isinstance(datasets, list):
            for dataset in datasets:
                if isinstance(dataset, dict):
                    print(dataset.get("title"))


if __name__ == "__main__":
    main()
