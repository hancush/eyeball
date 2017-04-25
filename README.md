# 👁 eyeball 👁

Here thar be a simple scraper that compares the dataset totals on [data.gov/metrics](https://www.data.gov/metrics) to those logged in the `archive.csv` file at the root of this repo and logs when they change.

## Requirements

* Python 3.x
* lxml (`pip install lxml`)
* requests (`pip install requests`)
* csvkit (`pip install csvkit`)

## Makin' data

#### If you have [GNU Make](https://www.gnu.org/software/make/)

```bash
make clean
make all
```

#### If you don't have Make 

Update `archive.csv` and `output/log.csv`.

```bash
python app.py
```

Then generate the summary file.

```bash
csvsql --query ' \
        SELECT \
          parent_agency, \
          subagency, \
          SUM(delta) AS net_difference \
        FROM log \
        GROUP BY subagency \
        ORDER BY SUM(delta) DESC' \
    output/log.csv > output/churn_summary.csv
```

## What am I looking at?

- `archive.csv` contains the dataset counts from the last time the scraper was run
- `outout/log.csv` is a running log of each time those counts changed, with `delta` being the net difference between the observed total from the scraper and the total in `archive.csv`
- `output/churn_summary.csv` is the net difference in dataset counts for each subagency between ~Jan. 24 and the last time the scraper was run

#### A note about dataset counts: 

"... A collection is a group of similar datasets--for example, if there's a dataset that's created every year--so you could have multiple year's worth of data counting as one dataset. Sometimes when agencies organize and group similar datasets as a collection, the total number on catalog.data.gov can decrease significantly when the actual data available has not changed."

tl;dr - A "loss" of records does _not_ always mean those records were deleted; they may have been reorganized.
