# Mattermost Customer Success Engineering Python Tools

This repo holds any Python scripts that the Mattermost Customer Success team uses, that might also be useful to the wider community.

All of these scripts will require Python, as well as the [mattermostdriver](https://vaelor.github.io/python-mattermost-driver/index.html) package.  This package can  typically be added to your environment through the user of: 

```shell
pip install mattermostdriver
```

## mm-user-activity.py

This script produces a CSV file of all current users, along with their related activity dates and authentication method.  

The script takes the following parameters:

Parameter | Description
--------- | -----------
`-h, --help` | Displays a help message and exists
`--siteurl SITEURL` | **REQUIRED** The URL of your Mattermost server (just the URL or IP address)
`--port PORT` | The port on which the Mattermost servier is listening (Default: 443)
`--scheme SCHEME` | The protocol scheme to use for communication with Mattermost.  Valid options are `http` or `https`. (Default: `https`)
`--outfile OUTFILE` | **REQUIRED** The path of the CSV file to be created.  Note that this file must not exist, otherwise the script will exit with an error.
`--tokenfile TOKENFILE` | **REQUIRED** The path to a file containing a [Personal Access Toekn](https://docs.mattermost.com/developer/personal-access-tokens.html) of a user with full admin privileges.  This file should contain nothing other than the access token.
`--team TEAM` | TheThe name of the team to query. Use the url-friendly version, not the Team Display Name. If omitted, defaults to all users.  
`--pagesize PAGESIZE` | The page size when querying for users. (Default: 100)
`--num_users NUM_USERS` | The total number of users to retrieve
`--sort OPTION` | **Only available in conjunction with a Team** The field used to sort return results. Valid values are `last_activity_at`, or `create_at`.
