# Q.U.A.I.L. QUAIL Universal Analytics of Informatic Linkages
This is a project used to pull down and analyze data from REDCap. It places the project
metadata and data into sqlite databases arranged by form.

![Python Version](https://img.shields.io/pypi/pyversions/Django.svg)
![Build Status](https://img.shields.io/codeship/d6c1ddd0-16a3-0132-5f85-2e35c05e22b1.svg)

```



   ____  _    _         _____ _      
  / __ \| |  | |  /\   |_   _| |     
 | |  | | |  | | /  \    | | | |     
 | |  | | |  | |/ /\ \   | | | |     
 | |__| | |__| / ____ \ _| |_| |____
  \___\_\\____/_/    \_\_____|______|

   Q.U.A.I.L. Universal Analytics of Informatic Linkages


```

# Installation
 ## TODO: Write Here

# Usage examples
  ## TODO: Write Here

# Development Setup
  ## TODO: Write Here

# How to contribute

1. Fork it (<https://github.com/ctsit/QUAIL>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request  

# Release History
  ## TODO: Write Here

# License
  ## TODO: Write Here

# Author(s)
  ## TODO: Write Here

# Issues
  ## TODO: Write Here

# Wiki  
  ## TODO: Write Here

# Meta (other)

## Detailed description of QUAIL and its motivations
* Scenario
Quilliam the quail wants a warehouse of data available to him which can link many
different types of data together. It is important as well that it is able to pull
down and analyze this data locally so that it can be backed up and reported on at
future points in time.

* Implementation
** Metadata
This project has a lot of metadata involved that describes what is in the system.
Therefore there needs to be a structured way to keep it around and instrospect it.
We use a sqlite3 database that can be attached to other databases in order to hold
this information

*** Getting started
You will need to fill out the correct redcap url and token into the settings.yaml
file so that the code knows where to look.

*** A note about subjects
In redcap, there is a 'primary id' for uniquely identifying subjects. According to
[[http://sburns.org/2013/07/22/intro-to-redcap-api.html][Ken Burns]] this is always the first value returned in a metadata request. Additionally
there can be a secondary_unique_field which is given in a project info export.

*** Limitations
- This has only been tested with longitudinal projects so far and none with repeat forms
- This process can work to have multiple redcaps in the same database, but one needs to
change the settings file for each one.

** Records
This project is also meant to pull down the records so that they can be arranged
in a way that makes querying easier. This process takes a long time depending
on the size of the redcap. You should use the `screen` or `tmux` commands.

The records will be saved in the `data_root` field of the settings.yaml. If this is
not provided, then it will save the records in a `records` directory in the location
that the code was run.

*** Directory structure
Here are some examples about where you would find information in a batch; all paths should
be prepended with whatever your data root is

| data                                                            | path                                                                        |
|-----------------------------------------------------------------+-----------------------------------------------------------------------------|
| the records for all subjects chemistry labs from redcap         | batch_name/redcap_data_files/chemistry_lab.json                             |
| the records for all subjects neuro labs from redcap             | batch_name/redcap_data_files/neuro_lab.json                                 |
| the records for all subjects neuro labs from redcap, in batch_2 | batch_2/redcap_data_files/neuro_lab.json                                    |

The batch name comes from a combination of the redcap name and the date it was pulled.
The event comes from the unique event name in redcap.
The instrument comes from the instrument name plus a '.json' extension.

** SQL metadata database
Each batch has a metadata database that contains information about the redcap.
This can be used to explore information about your redcap project and be used to
build queries on the data.db in the batch root.

*** Limitations
There are some parts of the code right now that do not utilize the metadata database
to its fullest. They often will process the raw redcap data instead. This should
be fixed so that there is one source of truth.

** SQL database of records

Utilizes sqlite3. Using the `SchemaBuilder` class the database schema is generated.
It has been tested with sqlite3 on a mac.

*** Schema
There are tables for each form.
Those tables have columns for each field and then two additional linking the subject and
event.

NOTE: there will be a form_complete field with every form which is not listed in the metadata.
This is something that is a redcap default and will come down with the records so it should be
saved in the database as well

my_redcap_form
| col                | type                 |
|--------------------+----------------------|
| sql_id             | integer primary keys |
| subject_id         | text foreign key     |
| my_field_name      | text                 |
| ...                | ...                  |
| my_last_field_name | text                 |
| form_complete      | text                 |

**** Checkboxes
Checkbox fields have a select_choices_or_calculations property in the metadata export.
These are of the form:

"VALUE, DISPLAY | ... | LAST_VALUE, LAST_DISPLAY"

It appears that the first comma is what delineates the value that is stored in the field
from the displayed value. NOTE that the display can contain multiple commas, it is simply the first
that separates the two.

These value display options are created in the sql database as lookup tables:

field_name
| col         | type             | note                                                |
|-------------+------------------+-----------------------------------------------------|
| export_name | text primary key | what the key will come back as when doing an export |
| display     | text             | second part of the select choices                   |
| value       | text             | first part of the select choices                    |


When pulling these records from redcap, the record object will have extra keys not listed in the metadata.
The format is "fieldname___value"; the important part is the three underscores. These separate
the checkbox fieldname from the value of the checkbox.

EX:

Which colors do you like?
- [X] red
- [ ] blue
- [X] green

The export for this would look like:
color___1: 1
color___2: 0
color___3: 1

We adopt the same thing for
**** Dropdowns
These are basically normal fields except they have their lookup values stored in the database.
Tables that are drop down lookups are prefixed with 'dropdown'

*** Limitations

- These sql databases are only able to take in redcap records at this point.
- The setup for these databases in terms of what the keys are is not very configurable.
There is work that will need to be done in order to make it automatically generate the
right primary keys and foreign key relationships
