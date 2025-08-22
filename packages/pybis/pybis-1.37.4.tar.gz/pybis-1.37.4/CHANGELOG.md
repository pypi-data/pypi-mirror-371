## Changes with pybis-1.37.4

- Improvements to Spreadsheet API
- Handling UnicodeDecodeError in spreadsheet property
- Added revert_deletions method
- Introduced method for getting eln url for entities
- Improvements to ServerInformation functionalities
- Extended supported timestamp formats to include timezones
- Improvements to property type display information

## Changes with pybis-1.37.3

- Fixes to get_children/get_parents methods

## Changes with pybis-1.37.2

- Fixes to Fast Upload 

## Changes with pybis-1.37.1

- Implemented Fast download V2
- Fixed dataset with parents creation
- Fixed type checking for python <3.10
- Added basic ELN Spreadsheet support
- Added support for new OBJECT property creation with OBJECT type limitation
- Refactored AttributeHolder class to include fetchOptions
- Refactored get_children and get_parents methods to pull data in case of missing fetchOptions

## Changes with pybis-1.37.0

- Changes to new_sample method to use v3api in all cases
- Refactored new_experiment documentation 
- Fixed delete vocabulary term method
- Fixed v1 dataset upload
- Fixed PropertyAssignment data frame creation
- Improved property data type validation 
- Improved get_project method 
- Added missing description parameter to new sample type method
- Added missing DATE property type
- Improvement to user.get_roles() method to present proper project identification
- Improvements to property assignment display
- Fixed clearing of vocabulary properties
- Improved setup script
- Fixed transaction commit function
- Fixed mount() method to work with PAT
- Fixed plugin updates
- Fixed new term creation

## Changes with pybis-1.36.3

- Refactored metaData and multiValue properties to be backwards-compatible.
- Refactored get_children/get_parents methods
- Refactored property formatting functionality 


## Changes with pybis-1.36.2

- Refactoring of the set_token method.
- Improvement to exception handling for dataset upload 
- Improvement to PAT functionality 

## Changes with pybis-1.36.1

- Amended get_*_types() method to be backwards-compatible
- Amended dataset upload functionality to support big files 
- Added multivalued properties support for objects, collections and datasets

## Changes with pybis-1.36.0

- Reverted breaking changes to dataset upload functionality
- Performance improvements to get_sample and get_samples methods 

## Changes with pybis-1.35.11

- Improvements to dataset upload performance

## Changes with pybis-1.35.10

- Fixed issue with changing properties for linked datasets 

## Changes with pybis-1.35.9

- Changed get_samples method to also include dataset ids depending on the params 

## Changes with pybis-1.35.8

- Fixed a typo in the set attribute method

## Changes with pybis-1.35.7

- Improvements to fast download scheme 

## Changes with pybis-1.35.6

- Added metaData attribute handling for sample, sampleType, experiment, experimentType, dataset, datasetType
- Fixed property assignment to a newly created sample type.
- Updated docs.
- Fixed sample.del_children() method.
- Fixed metaData attribute assignment case.

## Changes with pybis-1.35.5

- Implementation of array-type properties handling
- Fixed assignment of dynamic property plugins to property types 


## Changes with pybis-1.35.4

- Changes to internal implementation of data set download/upload to use OpenBIS V3 API
- Added TIMESTAMP property reformatting to fit formats supported by OpenBIS

## Changes with pybis-1.35.3

- Modified set_token() method to accept PersonalAccessToken object
- Minor code refactoring

## Changes with pybis-1.35.2

- Added rising an error when re-login fails

## Changes with pybis-1.35.1

- fix overriding parents/children when performing update using results from get_samples call

## Changes with pybis-1.35.0

- removal of deprecated 'cli'
- removal of 'click' dependency
- update of contact information

## Changes with pybis-1.34.6

- new option 'permanently' in the delete method in openbis_object.py

## Changes with pybis-1.34.2

- fix syslog error

## Changes with pybis-1.34.1

- better handling of configuration

## Changes with pybis-1.34.0

- better error handling when connecting to openBIS server
- add experimental support for datasets via cli

## Changes with pybis-1.33.2

- fix openbis.support.email key error
- raise error if invalid token is passed to constructor
- show more attributes for spaces and projects

## Changes with pybis-1.33.0

- add support for personal access tokens (PAT)
- fix default dataset kind (was PHYSICAL_DATA instead of PHYSICAL)
- refactor existing pyBIS code

## Changes with pybis-1.32.1

- fixing the issue with incorrectly named reference to DataSetKind.PHYSICAL

## Changes with pybis-1.32.0

- throw error when invalid token is assigned
- to not show an error message if stored token is invalid (just do not use it)
- fixed a bug which led to missing parents and children

## Changes with pybis-1.31.6

- automatically setting the project if only experiment was set

## Changes with pybis-1.31.5

- optimised error generation without assert

## Changes with pybis-1.31.4

- fix another exception when saving a sample with custom code

## Changes with pybis-1.31.3

- fix exception in sample.save

## Changes with pybis-1.31.1

- fixed a file download problem when filename contained special characters (e.g. #)

## Changes with pybis-1.31.0

- new entity-type methods: get_next_code() and get_next_sequence()
- allow to set code manually for samples of sampleType with autoGeneratedCode=True

## Changes with pybis-1.30.4

- fixed and optimised (deprecated) download_attachments()

## Changes with pybis-1.30.3

- Another code fix for create_data_frame() in pybis.py to make group ID and user ID separate

## Changes with pybis-1.30.2

- Possible issue fixes with data frame in create_data_frame() in entity_type.py
- Code fix for create_data_frame() in pybis.py to make group ID and user ID separate

## Changes with pybis-1.30.1

- fixed KeyError when creating an empty data frame

## Changes with pybis-1.30.0

- session management reworked

## Changes with pybis-1.20.5

- fixed same problems as 1.20.5
- wrong version published

## Changes with pybis-1.20.4

- fixed parents/children problem when get_samples(), get_datasets()
- sorted imports

## Changes with pybis-1.20.3

- deactivated debugging logs
- creation of property type accets vocabulary object

## Changes with pybis-1.20.2

- fixed omitted function parameter which could cause issues

## Changes with pybis-1.20.1

- improved search performance
- introduced lazy loading for Things.df and Things.objects, so all necessary, and potentially
  costly, computation takes place only when the user requests those properties

## Changes with pybis-1.20.0

- metadata for property_types can now be changed to:
    - {'custom_widget' : 'Word Processor'}
    - {'custom_widget' : 'Spreadsheet'}
- added documentation how to change the ELN settings
- removed deprecated update_sample()
- removed deprecated update_experiment()

## Changes with pybis-1.19.1

- add set_token() method to set a token and also store it locally

## Changes with pybis-1.19.0

- added caching for get_experiment
- included OR when providing codes/permIds for samples and datasets
- improved documentation
- fixed property assigning problem with newly created entity types

## Changes with pybis-1.18.12

- fixed rel_file_links, prepended /

## Changes with pybis-1.18.11

- added rel_file_links to datasets for embedding in ELN-LIMS

## Changes with pybis-1.18.10

- added deprecation warnings for components/containers and attachments
- added download_path and file_links to datasets

## Changes with pybis-1.18.9

- fixed problem when searching for experiments

## Changes with pybis-1.18.8

- fixed problem with 20.10 releases where samples could not be found using the permId

## Changes with pybis-1.18.7

- fixed entity_type caching problem

## Changes with pybis-1.18.6

- fixed create samples bug
- fixed zip upload bug

## Changes with pybis-1.18.5

- fixed deref bug for container
- added set and get methods for properties

## Changes with pybis-1.18.4

- fixed bug in returning identifiers (thanks, Fabian!)

## Changes with pybis-1.18.3

- prevent other users to read the saved token (chmod 600)
- fixed various pylint issues
- fixed «session no longer valid» message
- fixed search issues

## Changes with pybis-1.18.2

- added deletion to transaction

## Changes with pybis-1.18.1

- fixed del_parents() bug accidentally introduced in 1.18.0

## Changes with pybis-1.18.0

- speed improvement when searching for samples and dataSets and then cycling through the results
- implemented search for number comparison, date comparison, string comparison (<, >, <=, >=)
- implemented search for parents identities and properties
- fixed minor bugs when connecting

## Changes with pybis-1.17.4

- fixed another vocabularies update bug
- extended tests
- extended documentation

## Changes with pybis-1.17.3

- fixed vocabularies bug
- fixed updating vocabularies

## Changes with pybis-1.17.1

- fixed datastore bug

## Changes with pybis-1.17.0

- added caching for often used but rarely updated openBIS objects.
- if you need to create a lot of Samples, this will improve your speed a lot
- by default, caching is enabled

## Changes with pybis-1.16.2

- transaction.commit() now updates all added samples with their respective permIds

## Changes with pybis-1.16.1

- new_dataset bugfix

## Changes with pybis-1.16.0

- added support for batch creation of samples
- changed Python minimum requirement to Python 3.6
- new vocabulary and new property_type: internalNameSpace was removed
- this will cause possible incompatibilities with older versions of openBIS (< 20.10.x)

## Changes with pybis-1.15.1

- added support for date-searching
- bugfix in property-searching

## Changes with pybis-1.14.10

- bugfix when deleting dataSets
- some improvements with the documentation

## Changes with pybis-1.14.9

- quick fix of parse_jackson error in special circumstances

## Changes with pybis-1.14.7

- bugfix: no longer any error in get_samples(), get_datasets() and get_experiments() when
  properties are provided but no data was found

## Changes with pybis-1.14.6

- bugfix duplicate property-columns in get_samples() and get_datasets()

## Changes with pybis-1.14.5

- no automagic detection of mountpoint, because of Windows incompatibilities

## Changes with pybis-1.14.4

- added new convenience methods: get_experiments, get_projects etc.

## Changes with pybis-1.14.3

- small bugfix: prevent error

## Changes with pybis-1.14.2

- properties can be provided with either upper or lowercase
- bugfix of duplicate property columns

## Changes with pybis-1.14.1

- small bugfix

## Changes with pybis-1.14.0

- use props="\*" to get all properties of all samples or datasets

## Changes with pybis-1.13.0

- added symlink() method for datasets to automatically create symlinks
- added `is_symlink()` and `is_physical()` methods for dataSets
- new `o.download_prefix` attribute for `download()` and `symlink()`
- `download_prefix` defaults to `data/openbis-hostname`

## Changes with pybis-1.12.4

- fixed a bug which occured on some opeBIS instances when retrieving samples

## Changes with pybis-1.12.3

- datasets, samples and experiments now successfully return project and space attributes

## Changes with pybis-1.12.0

- added possibility to get any additional attributes in the get_samples() method
- added possibility to get any additional attributes in the get_dataSets() method

## Changes with pybis-1.11.1

- added automatically accepting host key, otherwise mount() will hang the first time

## Changes with pybis-1.11.0

- implemented mount() and unmount() methods to mount openBIS dataStore server via SSHFS and FUSE
- implemented is_mounted() and get_mountpoint() methods
- added instructions how to install FUSE/SSHFS on Unix systems

## Changes with pybis-1.10.8

- dataSets of kind CONTAINER now also allow download of files

## Changes with pybis-1.10.7

- made download work, even downloadUrl attribute is missing in dataSets

## Changes with pybis-1.10.6

- added possibility to download files without /original/DEFAULT folders

## Changes with pybis-1.10.5

- bugfix: creating projects

## Changes with pybis-1.10.4

- better error messages when downloading files from datastore server

## Changes with pybis-1.10.3

- print warning message when downloaded file-size does not match with promised file-size. Do not
  die.

## Changes with pybis-1.10.2

- typo bugfix

## Changes with pybis-1.10.1

- fixed a nasty threading bug: open threads are now closed when downloading or uploading datasets
- this bugfix avoids this RuntimeError: cannot start new thread

## Changes with pybis-1.10.0

- dataSet upload now supports zipfiles
- dataSet upload now supports files and folders
- different behaviour when providing a folder: files are no longer flattened out, structure is kept
  intact

## Changes with pybis-1.9.8

- new: create and update Dateset Types
- new: create and update Experiment Types
- new: create and update Material Types
- many bugfixes
- extended documentation about creating these entity types

## Changes with pybis-1.9.7

- bugfix for creating propertyTypes of type controlled vocabulary and material

## Changes with pybis-1.9.6

- bugfix when vocabulary attribute was not identical to the code of the aassigned property type

## Changes with pybis-1.9.5

- bugfixes: get_property_assignments() method fixed for dataSet-, experiment- and materialTypes

## Changes with pybis-1.9.4

- bugfix when searching for experiments or datasets of a given type

## Changes with pybis-1.9.3

- fixed documentation: add_members (not add_persons)
- bugfix role assignments of groups

## Changes with pybis-1.9.2

- searches for datasets and samples are highly improved
- search parameters can accept a code, an identifier or an openbis entity
- searching for all datasets in a project now works
- bugfixes

## Changes with pybis-1.9.1

- bugfix: controlled vocabulary

## Changes with pybis-1.9.0

- new: search, create, update and delete Property Types
- new: search, create, update and delete Plugins
- new: create and update Sample Types
- freeze entities to prevent changes
- added more tests

## Changes with pybis-1.8.5

- changed to v3 API when fetching datastores
- gen_permId to generate unique permIds used for dataSets
- support ELN-LIMS style identifiers: /SPACE/PROJECT/COLLECTION/OBJECT_CODE
- terms now can be moved either to the top or after another term

## Changes with pybis-1.8.4

- totalCount attribute added in every Things object
- totalCount will return the total number of elements matching a search
- bugfix in get_semantic_annotation method

## Changes with pybis-1.8.3

- new method for attributes: .attrs.all() will return a dict, much like .props.all()
- attributes like registrator and modifier are now returned by default

## Changes with pybis-1.8.2

- added key-lookup and setting for properties that contain either dots or dashes
- sample.props['some-weird.property-name'] = "some value"
- check for mandatory properties in samples (objects), datasets and experiments (collections)

## Changes with pybis-1.8.1

- revised documentation
- improved DataSet creation
- added missing delete function for DataSets
- wrong entity attributes will now immediately throw an error
- more DataSet creation tests
- paging tests added
- `collection` is now alias for `experiment`
- `object` is alias for `sample`

## Changes with pybis-1.8.0

- better support for fetching entity-types (dataSetTypes, sampleTypes)
- separation of propertyAssignments from entity-types
- added .get_propertyAssignments() method to all entity-types

## Changes with pybis-1.7.6

- bugfix dataset upload for relative files (e.g. ../../file or /User/username/file)
- always only the filename is added to the dataset, not the folder containing it
- corrected License file

## Changes with pybis-1.7.5

- added paging support for all search functions by providing start_with and count arguments
- make search more robust: allow get_sample('SPACE/CODE') instead of get_sample('/SPACE/CODE')
- make search more robust: allow get_sample(' 20160706001644827-208 ')
- make interface more robust (allow sample.permid instead of sample.permId)
- make properties more robust: allow get_samples(props='name') instead of get_samples(
  props=['name'])
- fixed bug when parent/children of more than one element was searched: o.get_experiments()
  .get_samples().get_parents()

## Changes with pybis-1.7.4

- pyBIS now allows to create dataset-containers that contain no data themselves
- datasets now show a «kind» attribute, which can be either PHYSICAL, LINK or CONTAINER
- PropertyAssignments and other internal data are now finally nicely presented in Jupyter
- various bugfixes
- README.md is now correctly displayed
- setup.py is fixed, installation should no longer fail because of some utf-8 problems on certain
  machines

## Changes with pybis-1.7.3

- improved packaging information
- LICENSE included (Apache License v.2)

## Changes with pybis-1.7.2

- added server_information to openBIS connection
- bugfix: project samples are only fetched when instance supports them

## Changes with pybis-1.7.1

- fixed bug in controlled vocabulary when property name did not match the vocabulary name
- added `xxx_contained()` methods to Samples and DataSets
- updated documentation

## Changes with pybis-1.7.0

- added components and containers functionality to both datasets and samples
- `set_attributes()` no longer automatically saves the object
- tags now have to be created (and saved) before they can be assigned
- `get_tag()` now can search for more than one tag at once and supports both code and permId
- `get_tags()` now available for almost all objects, returns a dataframe
- improved and enhanced documentation

## Changes with pybis-1.6.8

- fixed bugs with parents and children of both samples and datasets
- new samples can be defined with parents / children
- `get_parents()` and `get_children()` methods now also work on new, not yet saved objects
- `get_sample()` and `get_dataset()` now also accept arrays of permIds / identifiers
- pybis now has a CHANGELOG!
