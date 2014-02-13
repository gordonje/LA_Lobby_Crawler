from datetime import datetime
from time import sleep
from BeautifulSoup import BeautifulSoup
import requests
import re
import csv

start_time = datetime.now()
print "Started at " + str(start_time) + "..."

request_year = raw_input("Enter a four-digit year (or type 'All'): ")
request_month = raw_input("Enter a month (or type 'All'): ")

lobbyists = []

with open('lobbyists.csv', 'rU') as infile:
	reader = csv.reader(infile)
	for row in reader:
		lobbyists.append(row)

print str(len(lobbyists)) + " lobbyists loaded..."

def removeNonAscii(s):

    return "".join(i for i in s if ord(i)<128)


def report_scraper(lobbyist_id, branch, period, panel, date_label_id):

	report_header_data = [lobbyist_id, branch, period]

	date_label = panel.find(id = date_label_id)
	if date_label == None:
		report_header_data.append("")
	else:
		report_header_data.append(date_label.text.strip("Report Submitted: ."))

	with open('reports.csv', 'a') as outfile:
	    writer = csv.writer(outfile)
	    writer.writerow(report_header_data)
	    outfile.close()


def subjects_scraper(lobbyist_id, branch, period, panel, subjects_table_id):

	subject_table = panel.find("table", id = subjects_table_id)

	if subject_table <> None:
		for td in subject_table.findAll('td'):

			subject_name = td.text.strip()

			if subject_name.lower()[:10] <> 'no subject':
				
				with open('reports_subjects.csv', 'a') as outfile:
					writer = csv.writer(outfile)
					writer.writerow([lobbyist_id, branch, period, subject_name])
					outfile.close()


def expense_scraper(lobbyist_id, branch, period, panel, table_id, file_name):

	expense_table = panel.find("table", id = table_id)

	if expense_table == None:
		pass
	elif len(expense_table.findAll("tr")) == 1:
		pass
	else:

		for tr in expense_table.findChildren('tr')[1:]:
			new_expense = [lobbyist_id, branch, period]
			
			for td in tr.findChildren('td'):
				# confirm that this is the right way to remove ne lines, then add to the other functions
				new_expense.append(removeNonAscii(td.text.strip().replace('\n',' '))).
		
			with open(file_name + '.csv', 'a') as outfile:
				writer = csv.writer(outfile)
				writer.writerow(new_expense)
				outfile.close()


def spouse_child_scraper(lobbyist_id, branch, period, panel, table_id, file_name):

	spouse_child_table = panel.find("table", id = table_id)

	if spouse_child_table == None:
		pass
	elif len(spouse_child_table.findAll("span", id = re.compile(table_id + '_ctl\d+_Label1'))) == 0:
		pass
	else:

		for tr in spouse_child_table.findChildren('tr'):

			new_spouse_child_expense = [lobbyist_id, branch, period]

			official = tr.find("span", id = re.compile(table_id + '_ctl\d+_Label1')).text
			new_spouse_child_expense.append(removeNonAscii(official.strip()))

			if table_id == "ctl00_ContentPlaceHolder1_GridView5":
				city = tr.find("span", id = re.compile(table_id + '_ctl\d+_Label3')).text
				new_spouse_child_expense.append(removeNonAscii(city.strip("()")))

			if table_id == "ctl00_ContentPlaceHolder1_ExecDepExpGridView":
				department_agency = tr.find("span", id = re.compile(table_id + '_ctl\d+_Label3')).text
				department_agency = department_agency.split(", ")
				new_spouse_child_expense.append(removeNonAscii(department_agency[0].strip("(")))
				new_spouse_child_expense.append(removeNonAscii(department_agency[1].strip(")")))

			amount = tr.find("span", id = re.compile(table_id + '_ctl\d+_Label5')).text
			new_spouse_child_expense.append(removeNonAscii(amount))

			relation = tr.find("span", id = re.compile(table_id + '_ctl\d+_Label2')).text
			new_spouse_child_expense.append(removeNonAscii(relation.strip(" of")))

			with open(file_name + '.csv', 'a') as outfile:
				writer = csv.writer(outfile)
				writer.writerow(new_spouse_child_expense)
				outfile.close()


def amendment_scraper(lobbyist_id, branch, period, table_id):

	amendment_table = soup.find("table", id = table_id)

	if amendment_table == None:
		pass
	else:
		for tr in amendment_table.findChildren("tr")[1:]:
			new_amendment = [lobbyist_id, branch, period]

			for td in tr.findChildren("td"):
				new_amendment.append(removeNonAscii(td.text.strip()))

			with open('amendments.csv', 'a') as outfile:
				writer = csv.writer(outfile)
				writer.writerow(new_amendment)
				outfile.close()


session = requests.Session()
session.headers.update({"Connection": "keep-alive"})

for lobbyist in lobbyists[1:]:

	lobbyist_id = str(lobbyist[0])
	lobbyist_name = " ".join(i for i in lobbyist[1:4] if len(i)>0)

	years = []
	
	if request_year.lower() == 'all':

		payload = {'Period': '', 'LobID': lobbyist_id}
		response = session.get('http://ethics.la.gov/LobbyistData/LobbyistFinDiscl.aspx', params = payload)
		soup = BeautifulSoup(response.content)

		year_dropdown = soup.find("select", id = "ctl00_ContentPlaceHolder1_YearDropDownList")

		for option in year_dropdown.findChildren("option"):
			years.append(option.text)

		sleep(4)

	elif request_year == '2009':
		years.append('09')
	else:
		years.append(request_year)

	reporting_periods = []
	
	for year in years:

		if request_month.lower() == 'all':

			payload = {'Period': "January " + year, 'LobID': lobbyist_id}
			response = session.get('http://ethics.la.gov/LobbyistData/LobbyistFinDiscl.aspx', params = payload)
			soup = BeautifulSoup(response.content)

			year_dropdown = soup.find("select", id = "ctl00_ContentPlaceHolder1_YearDropDownList")

			selected_year = year_dropdown.findChild("option", selected="selected")

			if selected_year.text == year:

				reporting_period_dropdown = soup.find("select", id = "ctl00_ContentPlaceHolder1_RepPeriodDropDownList")

				for option in reporting_period_dropdown.findChildren("option")[1:]:
					reporting_periods.append(option.text)

			sleep(4)

		else:
			reporting_periods.append(request_month + " " + year)

	for period in reporting_periods:
		payload = {'Period': period, 'LobID': lobbyist_id}
		response = session.get('http://ethics.la.gov/LobbyistData/LobbyistFinDiscl.aspx', params = payload)
		soup = BeautifulSoup(response.content)

		reporting_period_dropdown = soup.find("select", id = "ctl00_ContentPlaceHolder1_RepPeriodDropDownList")
		selected_option = reporting_period_dropdown.findChild("option", selected="selected")

		exec_panel = soup.find(id = "ctl00_ContentPlaceHolder1_ExecPanel")
		if exec_panel <> None:

			branch = "Exec"

			report_scraper(lobbyist_id, branch, period, exec_panel, 'ctl00_ContentPlaceHolder1_ExecReportSubFormView_SubDateLabel')

			subjects_scraper(lobbyist_id, branch, period, exec_panel, 'ctl00_ContentPlaceHolder1_ExecSubjGridView')

			expense_scraper(lobbyist_id, branch, period, exec_panel, "ctl00_ContentPlaceHolder1_ExecGroupExpGridView", "executive_branch_group_expenses")

			expense_scraper(lobbyist_id, branch, period, exec_panel, "ctl00_ContentPlaceHolder1_ExecIndExpGridView", "executive_branch_expenses")

			spouse_child_scraper(lobbyist_id, branch, period, exec_panel, "ctl00_ContentPlaceHolder1_ExecDepExpGridView", "executive_branch_expenses")

			amendment_scraper(lobbyist_id, branch, period, "ctl00_ContentPlaceHolder1_ExecAmendGridView")

		leg_panel = soup.find(id = "ctl00_ContentPlaceHolder1_LegPanel")
		if leg_panel <> None:

			branch = "Leg"

			report_scraper(lobbyist_id, branch, period, leg_panel, 'ctl00_ContentPlaceHolder1_LegSubmitDateFormView_SubDateLabel')

			subjects_scraper(lobbyist_id, branch, period, leg_panel, 'ctl00_ContentPlaceHolder1_LegSubGridView')

			expense_scraper(lobbyist_id, branch, period, leg_panel, "ctl00_ContentPlaceHolder1_LegGroupGridView", "legislative_group_expenses")

			expense_scraper(lobbyist_id, branch, period, leg_panel, "ctl00_ContentPlaceHolder1_GridView1", "legislator_expenses")

			spouse_child_scraper(lobbyist_id, branch, period, leg_panel, "ctl00_ContentPlaceHolder1_GridView18", "legislator_expenses")

			expense_scraper(lobbyist_id, branch, period, leg_panel, "ctl00_ContentPlaceHolder1_GridView2", "public_servant_expenses")

			amendment_scraper(lobbyist_id, branch, period, "ctl00_ContentPlaceHolder1_LegAmendGridView")

		local_panel = soup.find(id = "ctl00_ContentPlaceHolder1_LocalPanel")
		if local_panel <> None:

			branch = "Local"

			report_scraper(lobbyist_id, branch, period, local_panel, 'ctl00_ContentPlaceHolder1_LocalReportSubmitFormView_SubDateLabel')

			subjects_scraper(lobbyist_id, branch, period, local_panel, 'ctl00_ContentPlaceHolder1_GridView3')

			expense_scraper(lobbyist_id, branch, period, local_panel, "ctl00_ContentPlaceHolder1_GridView6", "local_group_expenses")

			expense_scraper(lobbyist_id, branch, period, local_panel, "ctl00_ContentPlaceHolder1_GridView4", "local_official_expenses")

			spouse_child_scraper(lobbyist_id, branch, period, local_panel, "ctl00_ContentPlaceHolder1_GridView5", "local_official_expenses")

			amendment_scraper(lobbyist_id, branch, period, "ctl00_ContentPlaceHolder1_LocalAmendGridView")

		sleep(4)

	print "Completed " + lobbyist_name + ", Lobbyist ID: " + lobbyist_id + " [" + str(datetime.now()) + "]"


duration = datetime.now() - start_time

print "Finished in " + str(duration)