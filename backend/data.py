import pandas as pd

# Load S&P 500 constituent list and metadata from Wikipedia
# This will fetch the latest table each time the module is imported.
# Requires pandas and lxml/html5lib dependencies.

def _load_sp500():
    """
    Scrape the S&P 500 companies table from Wikipedia and return tickers and metadata.
    """
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    # Read the first table on the page, which contains the constituents
    df = pd.read_html(url, header=0)[0]
    # List of ticker symbols (keep original format, including dots)
    tickers = df['Symbol'].tolist()

    # List of ticker symbols
    tickers = df['Symbol'].tolist()

    # Metadata: map ticker -> { company, sector, sub_industry }
    metadata = {}
    for _, row in df.iterrows():
        metadata[row['Symbol']] = {
            'company': row['Security'],
            'sector': row['GICS Sector'],
            'sub_industry': row['GICS Sub-Industry'],
        }

    return tickers, metadata


# Exported variables
SP500_TICKERS, SP500_METADATA = _load_sp500()
