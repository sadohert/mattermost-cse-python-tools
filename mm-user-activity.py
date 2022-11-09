#!/usr/bin/python
import os
import argparse
from mattermostdriver import Driver
import json
from pathlib import Path


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file {} does not exist!".format(arg))
    else:
        return open(arg, 'r')  # return an open file handle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--siteurl", help="The site URL of the target Mattermost server")
    parser.add_argument(
        "--tokenfile", help="A txt file containing a valid Mattermost Personal Access token from an account with System Admin access.", type=lambda x: is_valid_file(parser, x))
    parser.add_argument(
        "--team", help="The name of the team to query.  Use the url-friendly version, not the Team Display Name")
    parser.add_argument(
        "--pagesize", help="The page size when querying for users", type=int, default=100)
    parser.add_argument(
        "--num_users", help="The total number of available users to retrieve", type=int, default=100)

    args = parser.parse_args()

    print("Site: {}, Token File: {}".format(args.siteurl, args.tokenfile))

    mm = Driver({'url': args.siteurl,
                'port': 443,
                 'token': args.tokenfile.readline().strip(),
                 'scheme': 'https',
                 'debug': True,
                 })

    mm.login()
    team_id = mm.teams.get_team_by_name(name=args.team)['id']

    # Page through users
    num_mm_users = mm.users.get_stats()['total_users_count']
    page_size = args.pagesize if num_mm_users > args.pagesize else num_mm_users
    page_count = (num_mm_users % page_size) + 1
    page_current_idx = 0
    print("Extracting information for {} users using - pagesize:{}, page_count:{}".format(
        num_mm_users, page_size, page_count))
    users_by_lastactivity = []
    while page_current_idx < page_count:
        users_by_lastactivity.extend(mm.users.get_users(
            params={'in_team': team_id, 'page': page_current_idx, 'per_page': page_size, 'sort': 'last_activity_at'}))
        page_current_idx += 1

    print([(t['username'], t['email']) for t in users_by_lastactivity])
    pass


if __name__ == "__main__":
    main()
