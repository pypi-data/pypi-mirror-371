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
from itertools import chain

from pandas import DataFrame

from .attribute import AttrHolder
from .openbis_object import OpenBisObject
from .things import Things
from .utils import (
    VERBOSE,
    extract_code,
    extract_id,
    extract_nested_identifier,
    extract_userId,
    parse_jackson,
)


class Person(OpenBisObject):
    """managing openBIS persons"""

    def __init__(self, openbis_obj, data=None, **kwargs):
        self.__dict__["openbis"] = openbis_obj
        self.__dict__["a"] = AttrHolder(openbis_obj, "person")

        if data is not None:
            self.a(data)
            self.__dict__["data"] = data

        if kwargs is not None:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    def __dir__(self):
        """all the available methods and attributes that should be displayed
        when using the autocompletion feature (TAB) in Jupyter
        """
        return [
            "permId",
            "userId",
            "firstName",
            "lastName",
            "email",
            "registrator",
            "registrationDate",
            "space",
            "get_roles()",
            "assign_role(role, space)",
            "revoke_role(role)",
        ]

    def get_roles(self, **search_args):
        """Get all roles that are assigned to this person.
        Provide additional search arguments to refine your search.

        Usage::
            person.get_roles()
            person.get_roles(space='TEST_SPACE')
        """
        roles = self.openbis.get_role_assignments(person=self, **search_args)
        groups = self.openbis.get_groups(userId=self.userId, **search_args)

        group_roles = chain.from_iterable(map(lambda x: x["roleAssignments"], groups.response["objects"]))
        count = len(roles) + groups.response["totalCount"]
        response_combined = roles.response["objects"] + list(group_roles)

        return Things(
            openbis_obj=self.openbis,
            entity="role_assignment",
            identifier_name="techId",
            start_with=0,
            count=0,
            totalCount=count,
            response=response_combined,
            df_initializer=self._create_role_assigment_data_frame,
        )

    def _create_role_assigment_data_frame(self, attrs, props, response):
        attrs = ["techId", "role", "roleLevel", "user", "group", "space", "project"]
        if len(response) == 0:
            roles = DataFrame(columns=attrs)
        else:
            objects = response
            parse_jackson(objects)
            roles = DataFrame(objects)
            roles["techId"] = roles["id"].map(extract_id)
            roles["user"] = roles["user"].map(extract_userId)
            roles["group"] = roles["authorizationGroup"].map(extract_code)
            spaces_s = roles["space"].map(extract_code)
            spaces_p = roles["project"].map(lambda x: x['space']['code'] if x is not None else '')
            roles["space"] = spaces_s + spaces_p
            roles["project"] = roles["project"].map(extract_nested_identifier)
        return roles[roles.columns.intersection(attrs)]

    def assign_role(self, role, **kwargs):
        try:
            self.openbis.assign_role(role=role, person=self, **kwargs)
            if VERBOSE:
                print(f"Role {role} successfully assigned to person {self.userId}")
        except ValueError as e:
            if "exists" in str(e):
                if VERBOSE:
                    print(f"Role {role} already assigned to person {self.userId}")
            else:
                raise ValueError(str(e))

    def revoke_role(self, role, space=None, project=None, reason="no reason specified"):
        """Revoke a role from this person."""

        techId = None
        if isinstance(role, int):
            techId = role
        else:
            query = {"role": role}
            if space is None:
                query["space"] = ""
            else:
                if isinstance(space, str):
                    query["space"] = space.upper()
                else:
                    query["space"] = space.code.upper()

            if project is None:
                query["project"] = ""
            else:
                if isinstance(project, str):
                    query["project"] = project.upper()
                else:
                    query["project"] = project.code.upper()

            # build a query string for dataframe
            querystr = " & ".join(f'{key} == "{value}"' for key, value in query.items())
            roles = self.get_roles().df
            if len(roles) == 0:
                if VERBOSE:
                    print(
                        f"Role {role} has already been revoked from person {self.code}"
                    )
                return
            techId = roles.query(querystr)["techId"].values[0]

        # finally delete the role assignment
        ra = self.openbis.get_role_assignment(techId)
        ra.delete(reason)
        if VERBOSE:
            print(f"Role {role} successfully revoked from person {self.code}")
        return

    def __str__(self):
        return f'{self.get("firstName")} {self.get("lastName")}'

    def delete(self, reason):
        raise ValueError("Persons cannot be deleted")

    def save(self):
        if self.is_new:
            request = self._new_attrs()
            resp = self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE:
                print("Person successfully created.")
            new_person_data = self.openbis.get_person(resp[0]["permId"], only_data=True)
            self._set_data(new_person_data)
            return self

        else:
            request = self._up_attrs()
            self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE:
                print("Person successfully updated.")
            new_person_data = self.openbis.get_person(self.permId, only_data=True)
            self._set_data(new_person_data)
