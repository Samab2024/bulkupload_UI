# new_api.py
import requests
import xml.etree.ElementTree as ET
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC as VeracodeHMAC

class veracode_api_call:
    def __init__(self, region, endpoint, creds, logger=None, params=None):
        self.logger = logger
        params = params or {}

        try:
            self.rownum = f"Line #{params.pop('rownum')}"
        except:
            self.rownum = 'TEST'

        self.url = self.get_url_from_endpoint(region, endpoint)
        self.auth = creds

        try:
            self.r = requests.get(url=self.url, auth=self.auth, params=params)
            self.log_activity()
        except requests.exceptions.RequestException as e:
            if self.logger:
                self.logger.error(f"[{self.rownum}] Request failed: {e}")
            else:
                print(f"[{self.rownum}] Request failed: {e}")
            raise

    def get_url_from_endpoint(self, region, endpoint):
        xml_version_numbers = {
            'beginprescan':'5.0', 'beginscan':'5.0', 'createapp':'4.0',
            'createbuild':'4.0', 'deleteapp':'5.0', 'deletebuild':'5.0',
            'getappinfo':'5.0', 'getapplist':'5.0', 'getbuildinfo':'5.0',
            'getbuildlist':'5.0', 'getfilelist':'5.0', 'getpolicylist':'5.0',
            'getprescanresults':'5.0', 'getvendorlist':'5.0', 'removefile':'5.0',
            'updateapp':'5.0', 'updatebuild':'5.0', 'uploadfile':'5.0',
            'detailedreport':'4.0', 'detailedreportpdf':'4.0', 'getappbuilds':'4.0',
            'getcallstacks':'5.0', 'summaryreport':'4.0', 'summaryreportpdf':'4.0',
            'thirdpartyreportpdf':'4.0', 'getmitigationinfo':'', 'updatemitigationinfo':'',
            'createsandbox':'5.0', 'getsandboxlist':'5.0', 'promotesandbox':'5.0',
            'updatesandbox':'5.0', 'createuser':'3.0', 'deleteuser':'3.0',
            'getuserinfo':'3.0', 'getuserlist':'3.0', 'updateuser':'3.0',
            'createteam':'3.0', 'deleteteam':'3.0', 'getteaminfo':'3.0',
            'getteamlist':'3.0', 'updateteam':'3.0', 'getcurriculumlist':'3.0',
            'gettracklist':'3.0', 'getmaintenancescheduleinfo':'3.0',
            'generateflawreport':'3.0', 'downloadflawreport':'3.0',
            'deletesandbox':'5.0'
        }

        if endpoint in xml_version_numbers:
            version = xml_version_numbers[endpoint]
            if region.upper() == 'EU':
                return f'https://analysiscenter.veracode.eu/api/{version}/{endpoint}.do'
            elif region.upper() == 'US':
                return f'https://analysiscenter.veracode.com/api/{version}/{endpoint}.do'
            else:
                raise ValueError("Region not supported. Please input EU/US.")
        else:
            # Fallback to elearning API
            return f'https://api.veracode.io/elearning/v1/{endpoint}'

    def log_activity(self):
        self.r.raise_for_status()

        if self.r.status_code == 401:
            if self.logger:
                self.logger.error(f"[{self.rownum}] 401 Unauthorized")
            else:
                print(f"[{self.rownum}] 401 Unauthorized")
        elif 'text/xml' in self.r.headers.get('content-type', ''):
            response = ET.fromstring(self.r.content)
            if response.tag == 'error':
                if self.logger:
                    self.logger.error(f"[{self.rownum}] {response.text}")
                else:
                    print(f"[{self.rownum}] {response.text}")
            else:
                if self.logger:
                    self.logger.info(f"[{self.rownum}] Success")
                else:
                    print(f"[{self.rownum}] Success")
        elif 'application/json' in self.r.headers.get('content-type', ''):
            if self.logger:
                self.logger.info(f"[{self.rownum}] JSON response received (processing not implemented)")
            else:
                print(f"[{self.rownum}] JSON response received (processing not implemented)")
        else:
            if self.logger:
                self.logger.info(f"[{self.rownum}] Unknown response type")
            else:
                print(f"[{self.rownum}] Unknown response type")