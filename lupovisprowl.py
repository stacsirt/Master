#!/usr/bin/env python3
# encoding: utf-8

from cortexutils.responder import Responder
from thehive4py.api import TheHiveApi
from thehive4py.models import CaseObservable
from thehive4py.query import Eq, And
from requests.auth import HTTPBasicAuth
import http.client as httplib
import json
import requests
import urllib3
import smtplib
import ssl
import sys
import re
urllib3.disable_warnings()

#Configure responder settings
class lupovisprowl(Responder):
    def __init__(self):
        Responder.__init__(self)
        self.case_id = self.get_param('data.id')
        self.data_type = self.get_param('dataType', default='unknown')
        self.thehive_url = self.get_param('config.thehive_url')
        self.thehive_key = self.get_param('config.thehive_key')
        self.thehive_cert = self.get_param('config.thehive_cert')
        self.thehive_api = TheHiveApi(self.thehive_url, self.thehive_key, self.thehive_cert)
        self.check_tlp = self.get_param('config.check_tlp', default=True)
        self.max_tlp = self.get_param('config.max_tlp', default=2)

    def run(self):
        Responder.run(self)

        hive_server = ""
        apikey = ''
        api = TheHiveApi(hive_server, apikey, cert=False)
        req = hive_server + "/api/case/artifact/_search"

        case_id = self.get_param('data.id', None, 'CaseId is missing')

        query = And(Eq('dataType', 'ip'))

        response = api.get_case_observables(case_id, query=query)
        observables = response.json()

        output = observables[0]['data']

        headers = {'Accept': 'application/json', 'x-api-key': ''}
        url = "https://api.prowl.lupovis.io/GetIPReputation?ip=" + output
        proxies = {}

        r = requests.get(url, headers=headers, proxies=proxies)

        self.report({"message": "IP Reputation check done"})

    def operations(self, raw):
        return [self.build_operation("AddTagToCase", tag=lupovisprowl)]

if __name__ == "__main__":
    lupovisprowl().run()