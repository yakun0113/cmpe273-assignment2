# cmpe273-assignment2

## Pre-requisites

* Install _Pipenv_

```
pip install pipenv
```

* Install _[Flask](https://palletsprojects.com/p/flask/)_

```
pipenv install flask==1.1.1
```

* Run your Flask application from a shell/terminal.

```sh
pipenv shell
$ env FLASK_APP=app.py flask run
```
## Requirements
When running app.py for the first time, a new database.db file (for SQLite) would be initialized, and all required tables will be created (in the init_db() function at line 34).

**To avoid creating duplicated tables in database, which may cause crash, in followup runs (of app.py), you would need to comment out inite_db() in app.py(in line 34).**

## Create a test

All the screenshots have been provided.

*Request*

Sample data is in "test_case.txt" if needed.
The result could be seen in the upload files "create_a_test.jpg" and "create_a_test_in_database.jpg"

```
POST http://localhost:5000/api/tests

{
    "subject": "Math",
    "answer_keys": {
        "1": "A",
        "2": "B",
        "3": "C",
        "..": "..",
        "49": "D",
        "50": "E"
    }
}
```

*Response*

```
201 Created

{
    "test_id": 1,
    "subject": "Math",
    "answer_keys": {
        "1": "A",
        "2": "B",
        "3": "C",
        "..": "..",
        "49": "D",
        "50": "E"
    },
    "submissions": [] 
}

```

## Upload a scantron
*Request*

The result could be seen in the upload files "upload_a_scantron.jpg" && "upload_a_scantron_in_database.jpg" 
"host_upload_file.jpg" shows the retrive of the upload scantron. 

```
curl -F 'data=@path/to/local/scantron-1.json' http://localhost:5000/api/tests/1/scantrons
```
*Response*


```
201 Created

{
    "scantron_id": 1,
    "scantron_url": "http://localhost:5000/files/scantron-1.json",
    "name": "Foo Bar",
    "subject": "Math",
    "score": 40,
    "result": {
        "1": {
            "actual": "A",
            "expected": "B"
        },
        "..": {
            "actual": "..",
            "expected": ".."
        },
        "50": {
            "actual": "E",
            "expected": "E"
        }
    }
}
```

## Check all scantron submissions
*Request*

The result could be seen in the upload files "check_all_scantron_submissions.jpg" && "submissions_with_score.jpg"

```
GET http://localhost:5000/api/tests/1
```
*Response*
```
{
    "test_id": 1,
    "subject": "Math",
    "answer_keys": {
        "1": "A",
        "2": "B",
        "3": "C",
        "..": "..",
        "49": "D",
        "50": "E"
    },
    "submissions": [
        {
            "scantron_id": 1,
            "scantron_url": "http://localhost:5000/files/1.pdf",
            "name": "Foo Bar",
            "subject": "Math",
            "score": 40,
            "result": {
                "1": {
                    "actual": "A",
                    "expected": "B"
                },
                "..": {
                    "actual": "..",
                    "expected": ".."
                },
                "50": {
                    "actual": "E",
                    "expected": "E"
                }
            }
        }
    ] 
}
