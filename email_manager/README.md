# Salty Gmailer
![GitHub release (with filter)](https://img.shields.io/github/v/release/ryanlong1004/salty_gmailer)

Salty Gmailer is a configuration based Gmail automation tool. Configuration is based off of YAML files that utilize
the Gmail search query (`q=...`) and the addition and subtraction of labels to manage emails.

See [here](https://support.google.com/mail/answer/7190?hl=en) for the library of search operators supported.

## Credentials
[Google Cloud Console](https://console.cloud.google.com/apis/credentials)

## Usage
```
usage: gmailer [-h] [paths ...]

Configuration based automation for gmail.

positional arguments:
paths path containing the rule.yaml files

options:
-h, --help show this help message and exit
```

Currently, the only arguments are locations of YAML configuration files.

For example, if you YAML configuration files were in a relative path to your current
location named `rules`, you would execute the program as
`gmailer ./rules`

## Configuration
See the following example of a YAML rule:

```
name: Trash
description: Sends messages to trash
search:
- older_than: 1m
- from: "github_ OR"
- from: notifications-noreply@linkedin.com
add_labels:
- TRASH
remove_labels:
```

Currently, name and description are for logging purposes only.  

`search` takes a list of key/value pairs to filter email messages to act on.  These are taken directly from the Gmail search
query operators.

`add_labels` is a list of labels to add that match the search criteria, while its inverse `remove_labels` will remove labels that match any search criteria.
This rule will find all emails older than 1 month that are from 'github_' or 'notifications-noreply@linkedin.com
' and adds the label 'TRASH' to any emails that match, trashing the emails. 







## TODO - Add Tox
