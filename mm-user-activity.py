#!/usr/bin/python
import os
import argparse
import datetime
from mattermostdriver import Driver
import json
from pathlib import Path

CSV_COLUMNS = ['id', 'create_at', 'update_at', 'delete_at', 'username', 'email', 'roles',
               'nickname', 'auth_service', 'first_name', 'last_name', 'position', 'last_activity_at']

DATE_COLUMNS = ['create_at', 'update_at', 'delete_at', 'last_activity_at']

DEFAULT_PORT = 443
DEFAULT_SCHEME = 'https'


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file {} does not exist!".format(arg))
    else:
        return open(arg, 'r')  # return an open file handle


def is_new_file(parser, arg):
    if os.path.exists(arg):
        parser.error(
            "The file {} already exists.  Choose a new filename".format(arg))
    else:
        return open(arg, 'w')  # return an open file handle


def formatuserjson(u, delim=', '):
    val = []
    val = [datetime.datetime.fromtimestamp(
        int(u.get(c))/1000) if c in DATE_COLUMNS and u.get(c) is not None else u.get(c) for c in CSV_COLUMNS]
    return delim.join(str(c).replace(",", " ") for c in val)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--siteurl", 
        help="The site URL of the target Mattermost server",
        required=True
    )
    parser.add_argument(
        "--port",
        default=DEFAULT_PORT,
        help="The port on which the Mattermost server is listening [Default: {0}]".format(DEFAULT_PORT)
    )
    parser.add_argument(
        "--scheme",
        default=DEFAULT_SCHEME,
        help="The HTTP scheme to be used. [Default: {0}]".format(DEFAULT_SCHEME),
        choices=['http', 'https']
    )
    parser.add_argument(
        "--outfile",
        help="The name of a file to output results to",
        required=True,
        type=lambda x: is_new_file(parser, x)
    )
    parser.add_argument(
        "--tokenfile",
        help="A txt file containing a valid Mattermost Personal Access token from an account with System Admin access.",
        required=True,
        type=lambda x: is_valid_file(parser, x)
    )
    parser.add_argument(
        "--team",
        help="""The name of the team to query.  Use the url-friendly version, not the Team Display Name.  
If omitted, defaults to all users."""
    )
    parser.add_argument(
        "--pagesize", help="The page size when querying for users", type=int, default=100)
    parser.add_argument(
        "--num_users", help="The total number of available users to retrieve", type=int)
    parser.add_argument(
        "--sort",
        help="""The field used to sort return results.  Valid values are [last_activity_at, create_at].
(Only used in conjunction with Team parameter, otherwise ignored.)
        """,
        default='last_activity_at',
        choices=['create_at', 'last_activity_at']
    )

    args = parser.parse_args()

    print("Site: {}, Token File: {}".format(args.siteurl, args.tokenfile))

    mm = Driver({'url': args.siteurl,
                'port': args.port,
                 'token': args.tokenfile.readline().strip(),
                 'scheme': args.scheme,
                 'debug': False,
                 })

    mm.login()
    if args.team:
        team_id = mm.teams.get_team_by_name(name=args.team)['id']

    # Page through users
    mm_total_users = mm.users.get_stats()['total_users_count']
    num_users_requested = mm_total_users if args.num_users is None else args.num_users

    page_size = args.pagesize if mm_total_users > args.pagesize else mm_total_users
    page_count = round(mm_total_users / page_size) + 1
    page_current_idx = 0
    num_users_retrieved = 0
    num_remaining_users = num_users_requested

    print("Extracting information for {} users using - pagesize:{}, page_count:{}".format(
        mm_total_users, page_size, page_count))
    users_json_array = []
    while num_users_retrieved < num_users_requested:
        req_params = {'page': page_current_idx, 'per_page': page_size}
        if args.team:
            req_params['in_team'] = team_id
            req_params['sort'] = args.sort
        users_json_array.extend(mm.users.get_users(
            params=req_params))
        print("Page: {}/{}".format(page_current_idx, page_count))
        num_users_retrieved += page_size
        page_current_idx += 1
        num_remaining_users -= page_size
        if num_remaining_users < page_size and num_remaining_users > 0:
            page_size = num_remaining_users

    # Save the file
    args.outfile.write("{}\n".format(", ".join(CSV_COLUMNS)))
    for u in users_json_array:
        args.outfile.write("{}\n".format(formatuserjson(u)))

    # print([(t['username'], t['email']) for t in users_json_array])
    pass


if __name__ == "__main__":
    main()
