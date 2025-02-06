This second iteration of the safeguarding report has been created for Umbrella environments that have integration with M365. 
As the user information can all be gathered from the Umbrella API, there is no need for calls to Meraki.

If the function is run at 00:00, A Jinja2 template is retrieved from an S3 bucket and loaded into memory. The program then adds the user information and blocked DNS 
requests to the table, creating the safeguarding report.
If the time is past 00:00, then the template is not loaded, but the report that was previously created with the days date.
Beautiful soup is used to parse the HTML of the report into memory, the latest information retrieved by the function is then appended to the current report table.
The report is then saved back to S3.

An AWS EentBridge event triggers the email function to run at 9:00am each weekday.
The email function takes the report from S3 then sends it directly attached to the specified recipients.