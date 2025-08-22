#   Copyright ETH 2018 - 2024 Zürich, Scientific IT Services
# 
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
# 
#        http://www.apache.org/licenses/LICENSE-2.0
#   
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
import datetime
import os
import re
import time
import uuid

import pytest
import filecmp
import tempfile

from pybis.things import Things


def test_get_datasets_count(space):
    o = space.openbis
    testfile_path = os.path.join(os.path.dirname(__file__), "testdir/testfile")
    dataset = o.new_dataset(
        type="RAW_DATA",
        experiment="/DEFAULT/DEFAULT/DEFAULT",
        files=[testfile_path],
        props={"$name": "some good name"},
    )
    dataset.save()

    try:
        current_datasets = o.get_datasets(count=1)
        assert current_datasets is not None
        assert len(current_datasets) == 1
    finally:
        dataset.delete("test_get_datasets_count", True)


def test_get_datasets_paging(space):
    o = space.openbis
    testfile_path = os.path.join(os.path.dirname(__file__), "testdir/testfile")
    dataset1 = o.new_dataset(
        type="RAW_DATA",
        experiment="/DEFAULT/DEFAULT/DEFAULT",
        files=[testfile_path],
        props={"$name": "some good name"},
    )
    dataset1.save()

    dataset2 = o.new_dataset(
        type="RAW_DATA",
        experiment="/DEFAULT/DEFAULT/DEFAULT",
        files=[testfile_path],
        props={"$name": "some good name"},
    )
    dataset2.save()

    try:
        current_datasets = o.get_datasets(start_with=1, count=1)
        assert current_datasets is not None
        assert len(current_datasets) == 1
    finally:
        dataset1.delete("test_get_datasets_paging", True)
        dataset2.delete("test_get_datasets_paging", True)


def test_create_datasets_no_file(space):
    o = space.openbis
    with pytest.raises(Exception) as exc:
        o.new_dataset(
            type="RAW_DATA",
            experiment="/DEFAULT/DEFAULT/DEFAULT",
            props={"$name": "some good name"},
        )
    assert str(exc.value) == "please provide at least one file"


def test_create_delete_dataset(space):
    timestamp = time.strftime("%a_%y%m%d_%H%M%S").upper()
    o = space.openbis
    testfile_path = os.path.join(os.path.dirname(__file__), "testdir/testfile")

    dataset = o.new_dataset(
        type="RAW_DATA",
        sample="/DEFAULT/DEFAULT/DEFAULT",
        files=[testfile_path],
        props={"$name": "some good name", "notes": "my notes"},
    )

    assert dataset is not None
    assert not dataset.permId
    assert dataset.p is not None
    assert dataset.p["$name"] == "some good name"
    assert dataset.p.notes == "my notes"

    with pytest.raises(Exception):
        dataset.non_existing_attribute = "invalid attribute"
        assert "attribute does not exist, should fail" is None

    with pytest.raises(Exception):
        dataset.p.non_existing_property = "invalid propery"
        assert "property does not exist, should fail" is None

    dataset.save()

    # now there should appear a permId in our object
    assert dataset.permId is not None
    permId = dataset.permId

    # get it by permId
    dataset_by_permId = o.get_dataset(dataset.permId)
    assert dataset_by_permId is not None
    assert dataset_by_permId.permId == permId
    assert dataset_by_permId.type is not None
    assert dataset_by_permId.type.code == "RAW_DATA"
    assert dataset_by_permId.kind == "PHYSICAL"
    assert dataset_by_permId.sample is not None
    assert dataset_by_permId.sample.code == "DEFAULT"
    assert dataset_by_permId.experiment is not None
    assert dataset_by_permId.experiment.code == "DEFAULT"

    assert dataset_by_permId.p is not None
    assert dataset_by_permId.p["$name"] == "some good name"
    assert dataset_by_permId.p.notes == "my notes"

    assert dataset_by_permId.registrator is not None
    assert dataset_by_permId.registrationDate is not None
    # check date format: 2019-03-22 11:36:40
    assert (
            re.search(
                r"^\d{4}\-\d{2}\-\d{2} \d{2}\:\d{2}\:\d{2}$",
                dataset_by_permId.registrationDate,
            )
            is not None
    )

    # delete datasets
    dataset.delete("dataset creation test on " + timestamp, True)

    # Give openbis some time to process it
    time.sleep(1)
    # check that permanent deletion is working
    deletions = o.get_deletions(0, 10)
    assert len(deletions) == 0

    # get by permId should now throw an error
    with pytest.raises(Exception):
        deleted_ds = o.get_dataset(permId)


def test_revert_deletion_dataset(space):
    timestamp = time.strftime("%a_%y%m%d_%H%M%S").upper()
    o = space.openbis
    testfile_path = os.path.join(os.path.dirname(__file__), "testdir/testfile")

    dataset = o.new_dataset(
        type="RAW_DATA",
        sample="/DEFAULT/DEFAULT/DEFAULT",
        files=[testfile_path],
        props={"$name": "some good name", "notes": "my notes"},
    )

    assert dataset is not None
    assert not dataset.permId
    assert dataset.p is not None
    assert dataset.p["$name"] == "some good name"
    assert dataset.p.notes == "my notes"

    dataset.save()

    # now there should appear a permId in our object
    assert dataset.permId is not None
    permId = dataset.permId

    # get it by permId
    dataset_by_permId = o.get_dataset(dataset.permId)
    assert dataset_by_permId is not None
    assert dataset_by_permId.permId == permId

    # delete datasets
    dataset.delete("dataset creation test on " + timestamp)

    # Give openbis some time to process it
    time.sleep(2)

    # get by permId should now throw an error
    with pytest.raises(Exception):
        deleted_ds = o.get_dataset(permId)
        assert "This should fail" is None

    df = o.get_deletions()
    assert df[df['permId'] == permId].empty is False
    deletionId = df[df['permId'] == permId]['deletionId'].iloc[0]
    o.revert_deletions([deletionId])

    dataset = o.get_dataset(permId)
    assert dataset is not None
    df = o.get_deletions()
    if df.empty is False:
        assert df[df['permId'] == permId].empty is True


def test_create_dataset_with_code(space):
    timestamp = time.strftime("%a_%y%m%d_%H%M%S").upper()
    o = space.openbis

    dataset = o.new_dataset(
        type="UNKNOWN",
        code=timestamp,
        experiment="/DEFAULT/DEFAULT/DEFAULT",
        sample="/DEFAULT/DEFAULT/DEFAULT",
        kind="CONTAINER",
    )

    assert dataset is not None
    assert not dataset.permId
    assert dataset.code == timestamp
    dataset.save()

    # our permId is now identical to the code we provided
    assert dataset.permId is not None
    assert dataset.permId == timestamp

    dataset.delete("dataset creation test on {}".format(timestamp))


def test_things_initialization(space):
    data_frame_result = [1, 2, 3]
    objects_result = [4, 5, 6]

    def create_data_frame(attrs, props, response):
        return data_frame_result

    def create_objects(response):
        return objects_result

    things = Things(
        openbis_obj=None,
        entity='dataset',
        identifier_name='permId',
        start_with=0,
        count=10,
        totalCount=10,
        response=None,
        df_initializer=create_data_frame,
        objects_initializer=create_objects
    )

    assert not things.is_df_initialised()
    assert not things.is_objects_initialised()

    assert things.df == data_frame_result
    assert things.objects == objects_result

    assert things.is_df_initialised()
    assert things.is_objects_initialised()


def test_create_new_dataset_v1(space):
    """Create dataset and upload file using upload scheme from before 3.6 api version"""
    openbis_instance = space.openbis

    testfile_path = os.path.join(os.path.dirname(__file__), "testdir/testfile")

    # It is a hack to force old way of upload for testing.
    openbis_instance.get_server_information()._info["api-version"] = "3.5"

    dataset = openbis_instance.new_dataset(
        type="RAW_DATA",
        experiment="/DEFAULT/DEFAULT/DEFAULT",
        files=[testfile_path],
        props={"$name": "some good name"},
    )
    dataset.save()
    print(dataset)
    assert dataset.permId is not None
    assert dataset.file_list == ["original/testfile"]


def test_create_new_dataset_v3_single_file(space):
    openbis_instance = space.openbis

    testfile_path = os.path.join(os.path.dirname(__file__), "testdir/testfile")

    dataset = openbis_instance.new_dataset(
        type="RAW_DATA",
        experiment="/DEFAULT/DEFAULT/DEFAULT",
        files=[testfile_path],
        props={"$name": "some good name"},
    )
    dataset.save()
    print(dataset)
    assert dataset.permId is not None
    assert dataset.file_list == ["original/testfile"]


def test_create_new_dataset_v3_directory(space):
    openbis_instance = space.openbis

    testfile_path = os.path.join(os.path.dirname(__file__), "testdir")

    dataset = openbis_instance.new_dataset(
        type="RAW_DATA",
        experiment="/DEFAULT/DEFAULT/DEFAULT",
        files=[testfile_path],
        props={"$name": "some good name"},
    )
    dataset.save()
    print(dataset)
    assert dataset.permId is not None
    assert len(dataset.file_list) == 2
    assert dataset.file_list[0].endswith('testdir/testfile')


def test_dataset_property_in_isoformat_date(space):
    o = space.openbis

    timestamp = time.strftime("%a_%y%m%d_%H%M%S").lower()

    # Create custom TIMESTAMP property type
    property_type_code = "test_property_type_" + timestamp + "_" + str(uuid.uuid4())
    pt_date = o.new_property_type(
        code=property_type_code,
        label='custom property of data type timestamp',
        description='custom property created in unit test',
        dataType='TIMESTAMP',
    )
    pt_date.save()

    # Create new dataset type
    type_code = "test_dataset_type_" + timestamp + "_" + str(uuid.uuid4())
    dataset_type = o.new_dataset_type(code=type_code)
    dataset_type.save()

    # Assign created property to new dataset type
    dataset_type.assign_property(property_type_code)

    # Create new dataset with timestamp property in non-supported format
    timestamp_property = datetime.datetime.now().isoformat()
    testfile_path = os.path.join(os.path.dirname(__file__), "testdir/testfile")

    dataset = o.new_dataset(
        type=type_code,
        experiment="/DEFAULT/DEFAULT/DEFAULT",
        files=[testfile_path],
        props={property_type_code: timestamp_property},
    )
    dataset.save()

    # New dataset case
    assert len(dataset.p()) == 1
    assert dataset.p[property_type_code] is not None

    # Update dataset case
    dataset.p[property_type_code] = timestamp_property
    dataset.save()

    assert len(dataset.p()) == 1
    assert dataset.p[property_type_code] is not None

def test_create_new_dataset_with_parent(space):
    openbis_instance = space.openbis

    testfile_path = os.path.join(os.path.dirname(__file__), "testdir/testfile")

    dataset = openbis_instance.new_dataset(
        type="RAW_DATA",
        experiment="/DEFAULT/DEFAULT/DEFAULT",
        files=[testfile_path],
        props={"$name": "some good name"},
    )
    dataset.save()

    assert dataset.permId is not None
    assert dataset.file_list == ["original/testfile"]

    new_dataset = openbis_instance.new_dataset(
        type="RAW_DATA",
        experiment="/DEFAULT/DEFAULT/DEFAULT",
        files=[testfile_path],
        props={"$name": "some good name"},
        parents=[dataset.permId]
    )
    new_dataset.save()

    assert new_dataset.permId is not None
    assert new_dataset.file_list == ["original/testfile"]
    assert new_dataset.parents == [dataset.permId]

def test_create_new_dataset_in_chunks(space):
    openbis_instance = space.openbis

    testfile_path = os.path.join(os.path.dirname(__file__), "testdir/testfile_big")

    dataset = openbis_instance.new_dataset(
        type="RAW_DATA",
        experiment="/DEFAULT/DEFAULT/DEFAULT",
        files=[testfile_path],
        props={"$name": "some good name"},
    )
    dataset.save()

    assert dataset.permId is not None
    assert dataset.file_list == ["original/testfile_big"]

    with tempfile.TemporaryDirectory() as tmpdirname:
        dataset.download(destination=tmpdirname, create_default_folders=False)
        assert filecmp.cmp(testfile_path, os.path.join(tmpdirname, "testfile_big"))

