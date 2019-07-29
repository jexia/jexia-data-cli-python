# Jexia data CLI #
Jexia-data-cli allows export/import data from/to the dataset. 

## Installation ##
1. Clone this repo;
2. Install requirements (`pip install -r requirements.txt`).

## How to use ##
Before using the utility you need:
1. [Create dataset](https://www.jexia.com/en/docs/getting-started/);
2. [Create additional user in UMS](https://www.jexia.com/en/docs/user-management/);
3. [Create a policy for this user](https://www.jexia.com/en/docs/user-management/) to read/write the dataset.

As a result you need to have data:
1. Project's UUID (in the example `4d0add8d-c969-468b-befa-cb2b3e170138`);
2. Name of dataset (in the example `test`);
3. Email and password for additional user.

After that you can export data by a command like:
`python jexia-data-cli.py -p 4d0add8d-c969-468b-befa-cb2b3e170138 -d test -t json -f ./test.json -e`

or import data by a command like:

`python jexia-data-cli.py -p 4d0add8d-c969-468b-befa-cb2b3e170138 -d test -t json -f ./test.json -i`

For more information, see help: `python jexia-data-cli.py -h`
