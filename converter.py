#!/usr/bin/env python
"""
Description goes here
"""
__author__ = "jupp"
__license__ = "Apache 2.0"
__date__ = "21/03/2018"

import json
import requests
import sys

DSS_DOMAIN = "dss"
HCA_DOMAIN = "data.humancellatlas.org"

def get_bundle(bundle_uuid):
    bundle_url = "https://{}.{}/v1/bundles/{}?replica=aws".format(
        DSS_DOMAIN, HCA_DOMAIN, bundle_uuid)
    r = requests.get(bundle_url)
    return r.json()


def get_file(file_uuid):
    file_url = "https://{}.{}/v1/files/{}".format(
        DSS_DOMAIN, HCA_DOMAIN, file_uuid)

    r = requests.get("{}{}".format(file_url, '?replica=aws'))
    file_content = r.json()
    return file_content


def convert_bundle(bundle):
    bundle_uuid = bundle['bundle']['uuid']

    filename_counter = {}
    for file in bundle['bundle']['files']:
        if "dcp-type=\"metadata/" in file['content-type']:
            content_type = file['content-type']
            file_uuid = file['uuid']
            file_content = get_file(file_uuid)

            if "project" in content_type:
                writeFile("project.json", file_content)
            elif "links" in content_type:
                writeFile("links.json", file_content)
            else:
                if "biomaterial" in content_type:
                    dump_list_items("biomaterials", file_content, filename_counter)
                elif "process" in content_type:
                    dump_list_items("processes", file_content, filename_counter)
                elif "protocol" in content_type:
                    dump_list_items("protocols", file_content, filename_counter)
                elif "file" in content_type:
                    dump_list_items("files", file_content, filename_counter)

def dump_list_items(name, file_content, filename_counter):
    for idx, val in enumerate(file_content[name]):
        name = get_schema_name(val)
        if name not in filename_counter:
            filename_counter[name] = 0
        else:
            filename_counter[name] += 1

        writeFile("{}_{}.json".format(name, str(filename_counter[name])), val)


def writeFile (name, objects):
    with open('output/'+name, 'w') as outfile:
        json.dump(objects, outfile, indent=4)

def get_schema_name(object):
    if "content" in object:
        if "describedBy" in object["content"]:
            return object["content"]["describedBy"].rsplit('/', 1)[-1]


def main(argv=sys.argv[1:]):
    bundle_uuid = argv[0]
    bundle = get_bundle(bundle_uuid)
    convert_bundle(bundle)


if __name__ == "__main__":
    print(sys.argv)
    main(sys.argv[1:])
