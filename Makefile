.PHONY : all scrape clean
all : output/churn_summary.csv

scrape :
	# Refreshes output/log.csv and archive.csv
	~/.virtualenvs/eyeball/bin/python app.py

output/churn_summary.csv : scrape output/log.csv
	csvsql --query "SELECT \
		  parent_agency, \
		  subagency, \
		  SUM(delta) AS net_difference \
		FROM log \
		GROUP BY subagency \
		ORDER BY SUM(delta) DESC" \
	$(word 2, $^) > $@

clean :
	rm output/churn_summary.csv
