# count-rfcs
A simple python tool to identify the contributions to RFCs for any IETF participant. It currently classifies RFCs in the following categories, in declining order of priority:

* Listed as author

* Document Shepherd

* Responsible AD

* Acknowledged somewhere in the text

* Submitted an IESG ballot that contained text (COMMENT or DISCUSS)

* Any document where the attempt to retrieve from the rfc-editor or datatracker failed for some reason.

Just type
'''
python3 count-rfcs.py
'''

To run it.

Change the parameters in the first code block to input the correct names.

These parameters also affect the speed at which things run. Every RFC that is not discarded due to being the wrong status, date, or area takes about 1 second to process, so if there are no filters whatsoever 10,000 RFC's will take ~3 hours.

Parameters:
* name: how the name would appear in the datatracker, or in a acknowledgements section (usually '[first name] [last name]')

* include_informational, include_experimental: set to False if you don't care about documents with this status

* include_acknowledgments: if True, the script will download and search the document itself to find your name

* first_year: the first year an RFC might of been published that the person affected (set to 1969 or earlier to disable)

* first_rfc: the earliest RFC number the person might have affected (set to 0000 to disable)

* last_rfc: skip over all RFC numbers beyond this (mostly useful for debugging)

* first_ad_year: the first year someone was an AD; before that year, the tool does not check if the person balloted on a draft. To disable, set it to a future year. Also, after first_ad_year the script ignores any limits on area, stream, or wg
The script will process an RFC that matches ANY of the lists below

* streams: before first_ad_year, the tool will check any RFC from this stream

* areas: before first_ad_year, the tool will check any RFC from the areas listed here

* wgs: before first_ad_year, the tool will check any RFC from wgs listed here. 'NON' is a reserved word for non-working-group IETF stream documents; 'IESG' is a reserved word too
