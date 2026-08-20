# Amazon Product Scraper

Simple Python project for collecting Amazon product ASINs and reading basic product information.

## Files

- `asin_collector.py` → collects ASINs from Amazon search results
- `product_scraper.py` → reads ASINs and fetches title, reviews and price
- `asins.txt` → generated ASIN list

## Install

```bash
pip install requests beautifulsoup4
```

## Usage

Collect ASINs:

```bash
python asin_collector.py
```

Read product information:

```bash
python product_scraper.py
```

## Performance

`product_scraper.py` uses multiple workers to process products faster.

Default:

```python
max_workers=20
```

If requests start failing, try lowering it to `10` or `5`.

## Note

Amazon page structure may change over time, so selectors may need to be updated.
