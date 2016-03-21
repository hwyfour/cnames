#!/usr/bin/env python
# -*- coding: utf-8 -*-

_about = '''
CNAMES discovers the CNAMEs of a list of URLs and builds two trees with the information:

Input: A CSV file with a URL on each line
Output: Two JSON files per URL, one tree per file, written into an output folder

Example:

    output/
        macys.com-url.json
        macys.com-cname.json

URL TREE:
    - Structured by reverse domain name notation with a traversal giving us the reversed URL.
    - Leaf nodes are defined as a key/value pair with the CNAME as the key and None as the value.

Example:

{
    "com": {
        "macys": {
            "www": {
                "www.macys.com.edgekey.net": None,
                "e108.a.akamaiedge.net": None
            },
            "m": {
                "www.macys.moovdns.net": None
            }
        }
    }
}

CNAME TREE:
    - Structured by reverse domain name notation with a traversal giving us the reversed CNAME.
    - Leaf nodes are defined as a key/value pair with the URL as the key and None as the value.

Example:

{
    "net": {
        "moovdns": {
            "macys": {
                "www": {
                    "m.macys.com": None
                }
            }
        }
    }
}

'''

import os
import sys
import json
import argparse
import dns.resolver

in_csv = os.path.join('examples', 'small.csv')
out_dir = 'output'


# split a string on . and return a reversed array of the split values
def to_reverse_array(url):
    return url.lower().split('.')[::-1]


# recursively build a tree for a given list of keys and a leaf value
def add(keys, tree, leaf):
    if len(keys) == 0:
        return

    key = str(keys[0])

    if key not in tree:
        tree[key] = {}

    if len(keys) == 1:
        tree[key][leaf] = None

    add(keys[1:], tree[key], leaf)

    return tree


def main(in_file_ptr, out_dir_ptr, verbose=False):
    with open(in_file_ptr, 'r') as in_file:

        resolver = dns.resolver.Resolver()
        # resolver.nameservers = ['8.8.8.8']

        for line in in_file:
            stripped = line.strip()

            if stripped == '':
                return

            print stripped

            urls = [
                'www.%s' % stripped,
                'm.%s' % stripped,
                'mobile.%s' % stripped
            ]

            # initialize empty trees for this URL
            url_tree = {}
            cname_tree = {}

            for url in urls:
                subs = [url]

                for sub in subs:
                    try:
                        answers = resolver.query(sub, 'CNAME')
                        for data in answers:
                            result = data.to_text()
                            if result[-1] == '.':
                                result = result[:-1]
                            # we want to further discover cnames, so add the result to the loop
                            subs.append(result)

                            # recursively add the result to the trees
                            url_tree = add(to_reverse_array(url), url_tree, result)
                            cname_tree = add(to_reverse_array(result), cname_tree, url)
                    except Exception as e:
                        pass

            url_json = json.dumps(
                url_tree,
                sort_keys = True,
                indent = 4,
                separators = (',', ': ')
            )

            cname_json = json.dumps(
                cname_tree,
                sort_keys = True,
                indent = 4,
                separators = (',', ': ')
            )

            if verbose:
                print url_json
                print cname_json

            try:
                # create URL tree for this URL
                with open(os.path.join(out_dir_ptr, '%s-url.json' % stripped), 'w') as url_out:
                    url_out.write(url_json)

                # create CNAME tree for this URL
                with open(os.path.join(out_dir_ptr, '%s-cname.json' % stripped), 'w') as cname_out:
                    cname_out.write(cname_json)
            except Exception as e:
                # probably an encoding error
                if verbose:
                    print 'Error writing trees for %s' % stripped, e


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=_about,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-i','--input', help='Input CSV')
    parser.add_argument('-o','--output', help='Output folder')
    parser.add_argument('-v','--verbose', help='Verbose', action='store_true')
    args = parser.parse_args()

    in_csv = args.input or in_csv
    out_dir = args.output or out_dir

    if not os.path.isfile(in_csv):
        parser.error('Input file does not exist.')

    if os.path.exists(out_dir) and not os.path.isdir(out_dir):
        parser.error('Invalid output directory.')

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    main(in_csv, out_dir, args.verbose)
