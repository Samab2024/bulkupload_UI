from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC as VeracodeHMAC
from new_api import veracode_api_call as api_call
from csv_in import csvIn
import traceback, logger, configparser, os, sys

def get_creds_profile(api_profile = None):
	api_profile = api_profile or input("Profile Name: ")

	config = configparser.ConfigParser(allow_no_value=True)
	config.read( os.path.join('.', 'credentials') )
	api_key_id = config.get(api_profile, 'VERACODE_API_KEY_ID')
	api_key_secret = config.get(api_profile, 'VERACODE_API_KEY_SECRET')
	return VeracodeHMAC(api_key_id, api_key_secret)

def bulkupload(region = None, api_profile = None, filename = None):
    region = region or input("Region: ")
    
    creds = get_creds_profile(api_profile)
    
    filename = filename or input("CSV File: ")
    myCSV = csvIn.fromFile(filename)
    myLogger = logger.Logger(filename)
	
	# Credentials Test to check validity; exit script if bad status code
    try:
        params = {'rownum': 'CredentialsTest'}
        call = api_call(region=region, endpoint='getmaintenancescheduleinfo', creds=creds, logger=myLogger, params=params )
		# call.r.raise_for_status()
    except Exception as e:
        myLogger.error('Bad response from Credentials test. Exiting...')
        sys.exit(e)

	# Loop through rows in CSV file
    lineinfo = myCSV.next()
    while lineinfo:
        if 'apiaction' in lineinfo:
            try:
                endpoint = lineinfo.pop('apiaction')
                call = api_call(region=region, endpoint=endpoint, creds=creds, logger=myLogger, params=lineinfo)
            except Exception as e:
                myLogger.error(e)
                myLogger.error( traceback.print_exc() )
        lineinfo = myCSV.next()

    myLogger.info("CSV completed. Exiting...")

def main(args):
    bulkupload()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
