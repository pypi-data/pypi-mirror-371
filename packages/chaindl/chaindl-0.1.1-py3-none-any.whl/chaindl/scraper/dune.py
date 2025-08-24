import pandas as pd
import cloudscraper
from urllib.parse import urlparse

def _download(url: str) -> pd.DataFrame:
    # Parse the query ID from URL
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2 or parts[0] != "queries":
        raise ValueError("URL is not a valid Dune query URL. Follow the guide at: https://chaindl.readthedocs.io/#dune-dune-com")
    query_id = int(parts[1])

    scraper = cloudscraper.create_scraper()

    # Get latest result set ID
    graphql_url = "https://dune.com/public/graphql"
    payload = {
        "operationName": "GetLatestResultSetIds",
        "variables": {"queryId": query_id, "parameters": [], "canRefresh": True},
        "query": """
                query GetLatestResultSetIds($canRefresh: Boolean!, $queryId: Int!, $parameters: [ExecutionParameterInput!]) {
                  resultSetForQuery(canRefresh: $canRefresh, queryId: $queryId, parameters: $parameters) {
                    completedExecutionId
                    failedExecutionId
                    pendingExecutionId
                    __typename
                  }
                }
            """
    }

    response = scraper.post(graphql_url, json=payload)
    if response.status_code != 200:
        raise ConnectionError(f"Failed to get result set ID: {response.status_code}")
    json_data = response.json()
    execution_id = json_data["data"]["resultSetForQuery"]["completedExecutionId"]
    if execution_id is None:
        raise ValueError("No completed execution found for this query.")

    # Fetch all execution data with pagination
    all_data = []
    offset = 0
    limit = 9999999

    execution_url = "https://core-api.dune.com/public/execution"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json",
        "Origin": "https://dune.com",
        "Referer": "https://dune.com/",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    while True:
        payload = {
            "execution_id": execution_id,
            "query_id": query_id,
            "parameters": [],
            "pagination": {"limit": limit, "offset": offset}
        }
        response = scraper.post(execution_url, headers=headers, json=payload)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch execution data: {response.status_code}")
        json_data = response.json()
        execution_result = json_data.get('execution_succeeded')
        if not execution_result:
            raise ValueError("Execution failed or no data returned.")

        data = execution_result['data']
        total_row_count = execution_result['total_row_count']
        all_data.extend(data)

        if len(all_data) >= total_row_count:
            break
        offset = len(all_data)

    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    return df
