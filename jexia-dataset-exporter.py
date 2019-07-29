#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import csv
import getpass
import json
import requests


DESCRIPTION = """
Jexia-dataset-exporter allows export/import data from/to the dataset. To use
exporter you need: 1. Create dataset; 2. Create additional user in UMS;
3. Create a policy for this user to read/write the dataset.
"""
AUTH_URL = "https://{}.app.jexia.com/auth"
DATASET_URL = "https://{}.app.jexia.com/ds/{}"
HEADERS = {"Content-Type": "application/json",
           "Accept": "application/json"}


class RequestError(Exception):

    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg

    @property
    def message(self):
        if (isinstance(self.msg, list) and self.msg
                and isinstance(self.msg[0], dict)
                and "message" in self.msg[0]):
            return self.msg[0]["message"]
        return self.msg


class HTTPRequest(object):

    def __init__(self, email, password, project):
        self.email = email
        self.password = password
        self.project = project
        self.token = None

    def auth_request(self, method, url, json=None):
        if not self.token:
            self._auth_ums()
        return self.request(url=url, method=method, json=json,
                            headers=dict(self.token, **HEADERS))

    def request(self, method, url, json=None, headers=None):
        if not headers:
            headers = HEADERS
        res = requests.request(method=method, url=url, headers=headers,
                               json=json, timeout=10)
        res_json = res.json()
        if res.status_code not in [200, 201]:
            raise RequestError(res_json)
        return res_json

    def _auth_ums(self):
        res = self.request(method="POST",
                           url=AUTH_URL.format(self.project),
                           json={"method": "ums",
                                 "email": self.email,
                                 "password": self.password})
        self.token = {"Authorization": "Bearer {}".format(res["access_token"])}


class Exporter(HTTPRequest):

    def __init__(self, email, password, project, type):
        super().__init__(email, password, project)
        self.project = project
        self.type = type

    def download(self, dataset, file):
        res = self.auth_request(method='GET',
                                url=DATASET_URL.format(self.project,
                                                       dataset))
        if self.type == "csv":
            self.write_as_csv(res, file)
        elif self.type == "json":
            self.write_as_json(res, file)

    def upload(self, dataset, file):
        data = None
        if self.type == "csv":
            data = self.read_as_csv(file)
        elif self.type == "json":
            data = self.read_as_json(file)
        self.auth_request(method='POST',
                          url=DATASET_URL.format(self.project, dataset),
                          json=data)

    def write_as_csv(self, data, file):
        self._remove_fields(data)
        data_to_write = list()
        data_to_write.append(data[0].keys())
        for el in data:
            data_to_write.append(el.values())
        with open(file, 'w') as f:
            writer = csv.writer(f)
            writer.writerows(data_to_write)

    def write_as_json(self, data, file):
        self._remove_fields(data)
        with open(file, 'w') as f:
            f.write(json.dumps(data))

    def read_as_csv(self, file):
        data = list()
        with open(file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data

    def read_as_json(self, file):
        with open(file, 'r') as f:
            return json.load(f)

    def _remove_fields(self, data):
        for el in data:
            for k in ["id", "created_at", "updated_at"]:
                del el[k]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("-p", "--project", required=True, type=str,
                        help="Project UUID")
    parser.add_argument("-d", "--dataset", required=True, type=str,
                        help="Name of dataset")
    parser.add_argument("-t", "--type", required=True, type=str,
                        choices=["csv", "json"], help="Input/output format")
    parser.add_argument("-f", "--file", required=True, type=str,
                        help="File with data")
    action_arg_group = parser.add_mutually_exclusive_group(required=True)
    action_arg_group.add_argument("-i", action="store_true",
                                  help="Import data to the dataset")
    action_arg_group.add_argument("-e", action="store_true",
                                  help="Export data from the dataset")
    args = parser.parse_args()
    # raw_input was renamed to input in Python 3.x
    try:
        input = raw_input
    except NameError:
        pass
    email = input("Please, enter email:\n")
    password = getpass.getpass("Please, enter password:\n")
    exporter = Exporter(email, password, args.project, args.type)
    try:
        if args.e:
            exporter.download(dataset=args.dataset, file=args.file)
        elif args.i:
            exporter.upload(dataset=args.dataset, file=args.file)
    except RequestError as err:
        print("Error: %s" % err.message)
