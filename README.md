LA_Lobby_Crawler
================

Intro
-----

LA-lobby-crawler is a custom web scraper for capturing information about expenditures disclosed by lobbyists to the [Louisiana Ethics Administration](http://ethics.la.gov/LobbyistData/ "Louisiana Ethics Administration") including the identity of lobbyist, the date, the dollar amount and which person or group was the benefactor. The goal is to aggregate all of this data into a series .csv files that can be imported into your database manager of choice (e.g., Access, MySQL), where you can analyze the extent to which lobbyists and their employers are exerting influence on Louisana legislators, executive branch agencies and local officials.

Before you use this...

There are several items you must have installed in order run this LA-lobby-crawler on your own computer:
* [Python 2.x]
* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/ "BeautifulSoup")
* [Requests](http://docs.python-requests.org/en/latest/ "Requests")

You should also be aware that LA-lobby-crawler needs a lot of uninterrupted time to do it's work. Even if you're only searching for expenditures for a single month, the script will still need two to three hours in order to complete. If you are trying to capture everything that's available, it will need to run for days, possibly an entire week.

Why so long? Well for starters, it has to make a single request for every lobbyist and every reporting period (i.e., year and month combination). When you consider the fact that there are over 1,200 lobbyists in the system, 12 months in a year and five plus years worth of data, we're talking about close to 75,000 requests. The actual number of requests the script sends, though, is drastically less (around 30,000) because it figures out in which reporting periods each lobbyist has filed an expenditure report and only submits requests for reports in that period for that lobbyist.

The main reason the LA-lobby-crawler takes so long is because it purposefully stalls for four seconds after each request. This was a necessary measure because, preditably, the LA Ethics Commission's server stops responding or throws one of several errors if requests are submitted in quick succession. Trial and error suggests that it will consistently tolerate one request every four seconds or slower.

If you need to get the data sooner and you're only insterested in the expenditures linked to specific lobbyists, you can limit your results by making a copy of the lobbyist.csv file, opening the original file, and deleting the records of lobbyist you wish to exclude from your search. Be sure you're modifying only the file named 'lobbyist.csv' because that's the name of the file the script is looking for.

About the scraper
-----------------

LA-lobby-crawler is a Python script which can be run through the command line. It incorporates several libraries, most of which are built into Python (e.g., 're' for Regex text pattern searching and 'csv' for reading and writing to .csv files). Though, there are a couple of key libraries that had to be installed separately:
* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/ "BeautifulSoup") for parsing the HTML of the response in order to capture only the data we want to keep.
* [Requests](http://docs.python-requests.org/en/latest/ "Requests") for submitting HTTP requests, in this case, exclusively GET.

LA-lobby-crawler collects information found on monthly expenditure reports filed by lobbyists, which are made available through the [Louisana Ethics Commission's Lobbying Portal](http://ethics.la.gov/LobbyistData/ "Louisana Ethics Commission's Lobbying Portal"). This includes itemized expenditures for which a specific public official or group was the benefactor and the subjects about which the lobbyist is lobbying. LA-lobby-crawler does not, however, discover information about who these lobbyists are or who they work for. Rather, a separate script was used to record each lobbyist's name and unique identifer and combined with other information available [here](http://ethics.la.gov/LobbyistData/ResultsByLobbyistForm.aspx?SearchParams=ShowAll&OrderBy=1 "here") in order to build the 'lobbyist.csv' file (see 'About the data' for more information). 

When the LA-lobby-crawler is executed, the user is first prompted to specify a four-digit year (or request 'all' years), then specify a month (or request 'all' months). The script then reads into memory all of the records from the lobbyist.csv file in the current directory, including the Commission's own unique numeric lobbyist identifier. It then establishes a single HTTP session through which all requests will be made.

Unless the user specifies to gather only expenditures for a single reporting period (e.g., just 'January 2014'), the script then submits an initial GET request with the Lobbyist_ID for that lobbyist's financial disclosure page. For example, here is the [financial disclosure page of Alton Ashy](http://ethics.la.gov/LobbyistData/LobbyistFinDiscl.aspx?Period=&LobID=268 "financial disclosure page of Alton Ashy"). There are two dropdowns on this page: 'Year' and 'Reporting Period', and the options within each dropdown will vary depending on which reporting periods the given lobbyist has expenditure reports available. In order to limit the number of requests, the script reads into memory all of the combinations of month and year that are valid for the given lobbyist that are also within the parameters provided by the user (e.g., if the user specified '2013' and 'all' months, the script figures out all of the months in 2013 for which the given lobbyist filed a report, and stores these in a Reporting_Period variable).

The script then makes a GET request for the expenditure report for each reporting period available for the given lobbyist, and the response to each of these requests is then broken down in several ways.

First, each lobbyist's expenditure report includes one to three sections (the code refers to these as 'panels') which correspond to one of the three branches of government -- executive, legislative and local -- which lobbyist may have lobbied during that reporting period. For each section that appears on the lobbyist's expenditure report, the script adds a record to 'reports.csv' specifying:
* the lobbyist's ID
* the branch of government that was lobbied
* the reporting period (month and year)
* the date that the report was filed

For each branch section, the script also records each of the subject matter lobbied in the 'reports_subject.csv' file.

Note that, for a given lobbyist's expenditure reports, the date the report was filed and the subject matters lobbied are almost always (are always?) the same. Though, there is the potential for this information to vary for each branch lobbied in a given reporting period, which is why it's recorded separately.

In each section of the report, the script then captures all expenditures that are listed. 

The expenditures collected in the executive branch section are:
* Expenditures attributable to individual executive branch officials, including the department and agency of the official, which are written to 'executive_branch_expenses.csv'
* Expenditures attributable to the spouse or minor child of an executive branch official, which are also written to 'executive_branch_expenses.csv'
* Expenditures made for receptions, social gatherings, or other functions to which more than 25 executive branch officials were invited, including the group (e.g., the department or office), the description of the event and the date of the event, which are written to 'executive_branch_group_expenses.csv'

The expenditures collected from the legislative branch section are:
* Expenditures attributable to individual legislators, which are written to 'legislator_expenses.csv'
* Expenditures attributable to individual public servants, which are written to 'public_servant_expenses.csv'
* Expenditures attributable to the spouse or minor child of a legislator, which are also written to 'legislator_expenses.csv'
* Expenditures made for receptions, social gatherings, or other functions to which the entire legislature, either house, any committee or sub-committee, caucus or delegation were invited, including the name of the group, the description of the event and the date of the event, which are written to 'legislative_group_expenses'

The expenditures collected from the local branch section are:
* Expenditures attributable to an individual local government officials, including the name of the local government group, such as a city or parish metro council, which are written to 'local_official_expenses.csv'
* Expenditures attributable to the spouse or minor child of a local government official, which are also written to 'local_official_expenses.csv'
* Expenditures made for receptions, social gatherings, or other functions to which more than 25 local government officials were invited, including the name of the local government agency, the description of the event and the date of the event, which are written to 'local_group_expenses.csv'

Finally, for each section, the script also captures itemized amendments that have subsequently been made to the given expenditure report, including the amendment was made and the description of the amendment. All amendments, regardless of the branch to which they are attributed, are written to 'amendments.csv'.

About the data
--------------

There are 11 main data files.

The 'lobbyists.csv' file contains a record for each lobbyist that was or is currently registered with the Louisiana Ethics Commission as of December 2013. The fields for these records are:
* Lobbyist_ID, which is an int field that serves as a unique identifier for each lobbyist.
* Firstname, which is a varchar field that stores the lobbyist's first name.
* Middlename, which is a varchar field that stores the lobbyist's middle name or middle initial.
* Lastname, which is a varchar field that stores the lobbyist's last name.
* Suffix, which is a varchar field that stores the lobbyist's name suffix (e.g., 'Jr.' or 'III').
* Branch, which is a varchar field that identifies which of the three branches of government the lobbyists is registered to lobbying, or if the lobbyist is not currently registered to lobby.
* Employer, which is a varchar field that identfies which organization the lobbyist is currently registered to lobby on behalf of.

The lobbyist records were obtained through a secondary script that makes a GET request for the financial disclosure page of lobbyist id 1 (in the url string, this is LobID=1). If there happens to be a lobbyist with an id of 1, then the script stores this number along with the lobbyist name found in the HTML response. The script then makes the same request for LobID=2, then LobID=3, and so on until it has identified 1,228 lobbyists, the number of records found in the [lobbyist information section](http://ethics.la.gov/LobbyistData/ResultsByLobbyistForm.aspx?SearchParams=ShowAll&OrderBy=1 "lobbyist information section") of the commission's lobbying portal.

The lobbyist's ID and name were then combined with records copied and pasted from the search by lobbyist information results. Microsoft Excel was use to manually match records and parse the name fields.

The 'reports.csv' file contains a record for each reporting period in which a given lobbyist filed an expenditure report and which branches of government he or she may have lobbied. Again, the lobbyist financial disclosure page is divide into one to three sections for each branch of government, and the records in this table correspond to those sections that appear for a given reporting period of a given lobbyist (see 'About the scraper' for more information). Note that there are many records in 'reports.csv' that have no corresponding records in any of the expenses tables, as these are cases when the lobbyist apparently filed an expenditure report indicating that he or she did not have any expenditures to disclose.

The fields on 'reports.csv' are:
* Lobbyist_ID, which is an int field that identfies which lobbyist filed the expenditure report.
* Period, which is a varchar field that contains the month and year for which the expenditure report was filed.
* Branch, which is a varchar field that identifies the branch of government ('Exec', 'Leg' or 'Local') that may have been lobbied by the given lobbyist in the given reporting period.
* Date_Sumbitted, which is a date field that specifies when the expenditure report was submitted.

The 'reports_subjects.csv' file contains a record for each subject about which a given lobbyist may have been lobbying in a given reporting period for a given branch of government. The distinct list of subjects is also available [here](http://ethics.la.gov/LobbyistData/Statistics/ChartSubjLobbied.aspx "here") in the commission's lobbying portal. Since lobbyists often list multiple subject on a given expenditure report, it isn't really possible to determine which itemized expenditures are relevant to which subjects.

The fields on 'reports_subjects.csv' are:
* Lobbyist_ID, which is an int field that identfies which lobbyist filed the expenditure report.
* Branch, which is a varchar field that identifies the branch of government ('Exec', 'Leg' or 'Local') that may have been lobbied by the given lobbyist in the given reporting period.
* Period, which is a varchar field that contains the month and year for which the expenditure report was filed.
* Subject_Name, which is a varchar field that contains one of the subject matters about which the given lobbyist may have been lobbying the given branch of government in the given reporting period.

Note that the Date_Submitted in 'reports.csv' and the records in 'reports_subjects.csv' are the only data that could potentially vary for any valid combination of Lobbyist_ID, Reporting_Period and Branch. However, this seems to rarely, if ever, be the case.

The 'executive_branch_expenses.csv' file contains a record for each expenditure attributable to individual executive branch officials or attributable to the spouse or minor child of an executive branch official. The fields on this file are:
* Lobbyist_ID, which is an int field that identfies which lobbyist filed the report that contained the expenditure.
* Period, which is a varchar field that contains the month and year for which the report containing the expenditure was filed.
* Official_Name, which is a varchar field containing the name of the official that benefited from the expenditure.
* Department, which is a varchar field containing the department where the official was working at the time.
* Agency, which is a varchar field containing the agency within the department where the official was working at the time.
* Amount, which is a decimal field containing the amount of money of the expenditure.
* Relation, which is a varchar field containing the relationship to the official (e.g., 'Spouse', 'Child') of the person who was the benefactor of an expenditure. Note that this field is blank for expenditures that directly benefitted public officials.

The 'executive_branch_group_expenses.csv' file contains a record for each expenditure made for receptions, social gatherings, or other functions to which more than 25 executive branch officials were invited. The fields on this file are:
* Lobbyist_ID, which is an int field that identfies which lobbyist filed the report that contained the expenditure.
* Period, which is a varchar field that contains the month and year for which the report containing the expenditure was filed.
* Group_Name, which is a varchar field that contains the name of the group (e.g., the department or office) which the officials were representing.
* Event_Description, which is a varchar field containing the description of the event.
* Event_Date, which is a date field containing the date of the event.
* Amount, which is a decimal field containing the amount of money of the expenditure.

The 'legislator_expenses.csv' file contains a record for each expenditure attributable to individual legislators or attributable to the spouse or minor child of a legislator. The fields on this file are:
* Lobbyist_ID, which is an int field that identfies which lobbyist filed the report that contained the expenditure.
* Period, which is a varchar field that contains the month and year for which the report containing the expenditure was filed.
* Official_Name, which is a varchar field that contains the name of the legislator that benefitted from the expenditure.
* Amount, which is a decimal field containing the amount of money of the expenditure.
* Relation, which is a varchar field containing the relationship to the legislator (e.g., 'Spouse', 'Child') of the person who was the benefactor of an expenditure. Note that this field is blank for expenditures that directly benefitted legislators.

The 'legislative_group_expenses' file contains a record for each expenditure made for receptions, social gatherings, or other functions to which the entire legislature, either house, any committee or sub-committee, caucus or delegation were invited. The fields on this file are:
* Lobbyist_ID, which is an int field that identfies which lobbyist filed the report that contained the expenditure.
* Period, which is a varchar field that contains the month and year for which the report containing the expenditure was filed.
* Group_Name, which is a varchar field that contains the name of the group (e.g., 'Legislative Rural Caucus', 'Senate Commerce Committee') which the legislators were representing.
* Event_Description, which is a varchar field containing the description of the event.
* Event_Date, which is a date field containing the date of the event.
* Amount, which is a decimal field containing the amount of money of the expenditure.

The 'public_servant_expenses.csv' file contains a record for each expenditure attributable to individual public servants (not legislators). The fields on this file are:
* Lobbyist_ID, which is an int field that identfies which lobbyist filed the report that contained the expenditure.
* Period, which is a varchar field that contains the month and year for which the report containing the expenditure was filed.
* Official_Name, which is a varchar field that contains the name of the public servant that benefitted from the expenditure.
* Amount, which is a decimal field containing the amount of money of the expenditure.

The 'local_official_expenses.csv' file contains a record for each expenditure attributable to an individual local government official or attributable to the spouse or minor child of a local government official. The fields on this file are:
* Lobbyist_ID, which is an int field that identfies which lobbyist filed the report that contained the expenditure.
* Period, which is a varchar field that contains the month and year for which the report containing the expenditure was filed.
* Official_Name, which is a varchar field that contains the name of the local official that benefitted from the expenditure.
* Amount, which is a decimal field containing the amount of money of the expenditure.
* Relation, which is a varchar field containing the relationship to the local official (e.g., 'Spouse', 'Child') of the person who was the benefactor of an expenditure. Note that this field is blank for expenditures that directly benefitted local officials.

The 'local_group_expenses.csv' file contains a record for each expenditure made for receptions, social gatherings, or other functions to which more than 25 local government officials were invited. The fields on this file are:
* Lobbyist_ID, which is an int field that identfies which lobbyist filed the report that contained the expenditure.
* Period, which is a varchar field that contains the month and year for which the report containing the expenditure was filed.
* Group_Name, which is a varchar field that contains the name of the group (e.g., 'Baton Rouge City Administration and Metro Council', 'Police Jury Association of Louisiana') which the legislators were representing.
* Event_Description, which is a varchar field containing the description of the event.
* Event_Date, which is a date field containing the date of the event.
* Amount, which is a decimal field containing the amount of money of the expenditure.

The 'amendments.csv' file contains a record for amendment that have subsequently been made to the given expenditure report. All amendments, regardless of the branch to which they are attributed, are written to this file. The fields on this file are:
* Lobbyist_ID, which is an int field that identfies which lobbyist filed the report that was amended.
* Branch, which is a varchar field that identifies the branch of government ('Exec', 'Leg' or 'Local') corresponds to the section of the expenditure report where the amendment appeared.
* Period, which is a varchar field that contains the month and year for which the report containing the expenditure was filed.
* Date, which is the date field represents when the amendment was filed.
* Description, which is a varchar field that contains the description of the amendment. For example, whether an expenditure was added or removed, the amount of the expenditure and which individual or group was the benefactor.

Verifying the results
---------------------

After importing the .csv files into your database manager, you can then verify that all available information was accurately captured by LA-lobby-crawler by running a series of aggregate queries. 

For example, in order confirm all the executive branch expenditure records, we can sub-select from each expense table (in this case, executive_branch_expenses and executive_branch_group_expenses) grouping by by period and summing the amount field, then unioning these results together and then grouping the union results by period and summing the amount field:

We can then compare these monthly numbers to those that appear in the [Reported Lobbying Expenditures by Month and Branch Lobbied chart](http://ethics.la.gov/LobbyistData/Statistics/ChartTotalExpenditures.aspx "Reported Lobbying Expenditures by Month and Branch Lobbied chart"), which is also in the LA Ethics Commission's Lobbying Portal.

In most cases, the monthly sum of amounts should match right down to the cent. However, you may find cases in which the results from the aggregate query are less than those that appear lobbying portal's chart. You can investigate each of these problems further by doing a similar aggregate query as the one above, only this time filtering down the reporting period in which the numbers don't match and grouping by Lobbyist_ID, First_Name and Last_Name:

You can then compare the results of this query to a [search by expenditure reports](http://ethics.la.gov/LobbyistData/SearchByFinancialDisclosure.aspx "search by expenditure reports") in commission's lobbying portal, in which you select the reporting period and branch in question and sort by lobbyist name, and figure out where the discrepencies exist.

Phantom lobbyist reports
------------------------

By following the process described in the previous section, a pattern of problems has been discovered which we like to call the 'phantom lobbyist report' problem. These are cases in which there seem to be expenditures linked to reports that cannot be access through the LA Ethics Commission's Lobbying Report. However, these expenditures are included in the [Reported Lobbying Expenditures by Month and Branch Lobbied chart](http://ethics.la.gov/LobbyistData/Statistics/ChartTotalExpenditures.aspx "Reported Lobbying Expenditures by Month and Branch Lobbied chart"), and appear in the [search by expenditure reports](http://ethics.la.gov/LobbyistData/SearchByFinancialDisclosure.aspx "search by expenditure reports") results.

To illustrate this problem, run a search by expenditure reports in which you enter 'Kristin Batulis' in the Lobbyist Name field, select 'Feruary 2013' from the Report Period dropdown and 'Executive' for the Branch dropdown.

You should get three results, each linked to a different executive branch official. But if you click on one of the 'February 2013' links in the Report Period column, you'll be taken to Kristin Batulis' financial disclosure page, but February 2013 will not be selected in the Reporting Period dropdown. In fact, you can't select 'February 2013', as this option does not appear.

In order to correct for the phantom lobbyist report problem, you can import the records in the following files into the appropriate tables:
* missing_group_local.csv
* missing_ind_exec.csv
* missing_group_exec.csv
* missing_ind_leg.csv
* missing_group_leg.csv
