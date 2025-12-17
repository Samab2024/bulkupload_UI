import requests, logger
import xml.etree.ElementTree as ET
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC as VeracodeHMAC

class veracode_api_call():
	def __init__(self, region, endpoint, creds = None, logger = logger.Logger(), params = []):
		self.logger = logger

		self.region = region
        
		try: self.rownum = 'Line #%s' % (params.pop('rownum'))
		except: self.rownum = 'TEST'

		self.url = self.get_url_from_endpoint(region, endpoint)

		if creds == None:
			self.auth=VeracodeHMAC(profile = None)
		else: self.auth=(creds)

		self.r = requests.get(url=self.url, auth=self.auth, params=params)

		self.log_activity()

	def get_url_from_endpoint(self, region, endpoint):
		xml_version_numbers = dict(beginprescan='5.0', beginscan='5.0', createapp='4.0', \
			createbuild='4.0', deleteapp='5.0', deletebuild='5.0', getappinfo='5.0', \
			getapplist='5.0', getbuildinfo='5.0', getbuildlist='5.0', getfilelist='5.0', \
			getpolicylist='5.0', getprescanresults='5.0', getvendorlist='5.0', \
			removefile='5.0', updateapp='5.0', updatebuild='5.0', uploadfile='5.0', \
			detailedreport='4.0', detailedreportpdf='4.0', getappbuilds='4.0', \
			getcallstacks='4.0', summaryreport='4.0', summaryreportpdf='4.0', \
			thirdpartyreportpdf='4.0', getmitigationinfo='', updatemitigationinfo='', \
			createsandbox='5.0', getsandboxlist='5.0', promotesandbox='5.0', updatesandbox='5.0', \
			createuser='3.0', deleteuser='3.0', getuserinfo='3.0', getuserlist='3.0', \
			updateuser='3.0', createteam='3.0', deleteteam='3.0', getteaminfo='3.0', \
			getteamlist='3.0', updateteam='3.0', getcurriculumlist='3.0', gettracklist='3.0', \
			getmaintenancescheduleinfo='3.0', generateflawreport='3.0', downloadflawreport='3.0', \
			deletesandbox='5.0')

		if endpoint in xml_version_numbers:
            		if region == 'EU':
                		return '%s/%s/%s.do' % ('https://analysiscenter.veracode.eu/api', xml_version_numbers[endpoint], endpoint)
            		elif region == 'US':  
                		return '%s/%s/%s.do' % ('https://analysiscenter.veracode.com/api', xml_version_numbers[endpoint], endpoint)
            		else:
                		print("Region not Supported. Please input EU/US")
                		exit(1)
		else:
			return '%s/%s' % ('https://api.veracode.io/elearning/v1/', endpoint)

	def log_activity(self):
		self.r.raise_for_status()
		if self.r.status_code == 401:
			self.logger.error( "[{0}]{1}".format(self.rownum, "401 Unauthorized") )
		elif 'text/xml' in self.r.headers.get('content-type'):
			response = ET.fromstring(self.r.content)
			if response.tag == 'error':
				self.logger.error( "[{0}]{1}".format(self.rownum, response.text) )
			else:
				self.logger.info( "[{0}]{1}".format(self.rownum, 'Success')	)
		elif 'application/json' in self.r.headers.get('content-type'):
			self.logger.info( "[{0}]{1}".format(self.rownum, 'Unsure how to process JSON') )
		else:
			self.logger.info( "[{0}]{1}".format(self.rownum, 'Unsure how to process response') )

	def print_response_info(self):
		print ('>>> r.status_code')
		print (self.r.status_code)
		print ('>>> r.encoding')
		print (self.r.encoding)
		print (">>> r.headers.get('content-type')")
		print (self.r.headers.get('content-type'))
		print ('>>> r.text')
		print (str(self.r.text))
