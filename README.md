# count-rfcs
A simple python tool to identify the contributions to RFCs for any IETF participant. It currently classifies RFCs in the following categories, in declining order of priority:

* Listed as author

* Document Shepherd

* Responsible AD

* Acknowledged somewhere in the text

* Submitted an IESG ballot that contained text (COMMENT or DISCUSS)

Just type
'''
python3 count-rfcs.py
'''

To run it.

Change the parameters in the first code block to input the correct names.

These parameters also affect the speed at which things run. Every RFC that is not discarded due to being the wrong status, date, or area takes about 1 second to process, so if there are no filters whatsoever 10,000 RFC's will take ~3 hours.

Parameters:
* name: in the format '[first initial] [last name]'. How the name appears as an author

* full_name: how the name would appear in the datatracker, or in a acknowledgements section (usually '[first name] [last name]')

* first_rfc: the earliest RFC number the person might have affected (set to 0000 to disable)

* include_informational, include_experimental: set to False if you don't care about documents with this status

* first_year (in progress): the first year an RFC might of been published that the person affected (set to 1969 or earlier to disable)

* first_ad_year (in progress): the first year someone was an AD; before that year, the tool does not check if the person balloted on a draft. To disable, set it to a future year

* areas (in progress): before first_ad_year, the tool will only check RFCs from areas listed here

* wgs (in progress): before first_ad_year, the tool will only check RFCs from wgs listed here (unless they fall in an area listed in 'areas')
