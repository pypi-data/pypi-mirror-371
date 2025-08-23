import ldap
import ldap.modlist
import sys
from ldap.ldapobject import LDAPObject
from pathlib import Path
from typing import Final, TextIO
from pypomes_core import (
    APP_PREFIX, TEMP_FOLDER,
    env_get_str, env_get_int, env_get_path, exc_format
)

_val: str = env_get_str(key=f"{APP_PREFIX}_LDAP_BASE_DN")
LDAP_BASE_DN: Final[str] = None if _val is None else _val.replace(":", "=")
_val = env_get_str(key=f"{APP_PREFIX}_LDAP_BIND_DN")
LDAP_BIND_DN:  Final[str] = None if _val is None else _val.replace(":", "=")
LDAP_BIND_PWD:  Final[str] = env_get_str(key=f"{APP_PREFIX}_LDAP_BIND_PWD")
LDAP_SERVER_URI:  Final[str] = env_get_str(key=f"{APP_PREFIX}_LDAP_SERVER_URI")
LDAP_TIMEOUT:  Final[int] = env_get_int(key=f"{APP_PREFIX}_LDAP_TIMEOUT",
                                        def_value=30)
LDAP_TRACE_FILEPATH:  Final[Path] = env_get_path(key=f"{APP_PREFIX}_LDAP_TRACE_FILEPATH",
                                                 def_value=TEMP_FOLDER / f"{APP_PREFIX}_ldap.log")
LDAP_TRACE_LEVEL:  Final[int] = env_get_int(key=f"{APP_PREFIX}_LDAP_TRACE_LEVEL",
                                            def_value=0)


def ldap_init(server_uri: str = LDAP_SERVER_URI,
              trace_filepath: Path = LDAP_TRACE_FILEPATH,
              trace_level: int = LDAP_TRACE_LEVEL,
              errors: list[str] = None) -> LDAPObject:
    """
    Initialize and return the LDAP client object.

    :param server_uri: URI to access the LDAP server
    :param trace_filepath: path for the trace log file
    :param trace_level: level for the trace log
    :param errors: incidental error messages
    :return: the LDAP client object
    """
    # initialize the return variable
    result: LDAPObject | None = None

    try:
        # retrieve/open the trace log  output device
        trace_out: TextIO
        match trace_filepath:
            case "sys.stdout" | None:
                trace_out = sys.stdout
            case "sys.stderr":
                trace_out = sys.stderr
            case _:
                trace_out = Path.open(trace_filepath, "a")

        if not isinstance(trace_level, int):
            trace_level = 0

        # obtain the connection
        result = ldap.initialize(uri=server_uri,
                                 trace_level=trace_level,
                                 trace_file=trace_out)
        # configure the connection
        result.set_option(option=ldap.OPT_PROTOCOL_VERSION,
                          invalue=3)
        result.set_option(option=ldap.OPT_REFERRALS,
                          invalue=0)
        result.set_option(option=ldap.OPT_TIMEOUT,
                          invalue=LDAP_TIMEOUT)
    except Exception as e:
        if isinstance(errors, list):
            errors.append(f"Error initializing the LDAP client: {__ldap_except_msg(e)}")

    return result


def ldap_bind(ldap_client: LDAPObject,
              bind_dn: str = LDAP_BIND_DN,
              bind_pwd: str = LDAP_BIND_PWD,
              errors: list[str] = None) -> bool:
    """
    Bind the given LDAP client object *conn* with the LDAP server, using the *DN* credentials *bind_dn*.

    :param ldap_client: the LDAP client object
    :param bind_dn: DN credentials for the bind operation
    :param bind_pwd: password for the bind operation
    :param errors: incidental error messages
    :return: True if the bind operation was successful, False otherwise
    """
    # initialize the return variable
    result: bool = False

    # perform the bind
    try:
        ldap_client.simple_bind_s(who=bind_dn,
                                  cred=bind_pwd)
        result = True
    except Exception as e:
        if isinstance(errors, list):
            errors.append(f"Error binding with the LDAP server: {__ldap_except_msg(e)}")

    return result


def ldap_unbind(ldap_client: LDAPObject,
                errors: list[str] = None) -> None:
    """
    Unbind the given LDAP client object *conn* with the LDAP server.

    :param ldap_client: the LDAP client object
    :param errors: incidental error messages
    """
    try:
        ldap_client.unbind_s()
        # is the log device 'stdout' ou 'stderr' ?
        # noinspection PyProtectedMember
        if ldap_client._trace_file.name not in ["<stdout>", "<stderr>"]: # noqa SLF001
            # no, close the log device
            # noinspection PyProtectedMember
            ldap_client._trace_file.close() # noqa SLF001
    except Exception as e:
        if isinstance(errors, list):
            errors.append(f"Error unbinding with the LDAP server: {__ldap_except_msg(e)}")


def ldap_add_entry(entry_dn: str,
                   attrs: dict,
                   errors: list[str] = None) -> None:
    """
    Add an entry to the LDAP store.

    :param entry_dn: the entry DN
    :param attrs: the entry attributes
    :param errors: incidental error messages
    """
    # obtain the LDAP client object
    ldap_client: LDAPObject = ldap_init(errors=errors)

    if ldap_client:
        if not isinstance(errors, list):
            errors = []
        # bind the LDAP client with the LDAP server
        bound: bool = ldap_bind(ldap_client=ldap_client,
                                errors=errors)
        if not errors:
            ldiff: list[tuple[any, any]] = ldap.modlist.addModlist(attrs)
            try:
                ldap_client.add_s(dn=entry_dn,
                                  modlist=ldiff)
            except Exception as e:
                errors.append(f"Error on the LDAP add entry operation: {__ldap_except_msg(e)}")

        # unbind the LDAP client
        if bound:
            ldap_unbind(errors=errors,
                        ldap_client=ldap_client)


def ldap_modify_entry(entry_dn: str,
                      mod_entry: list[tuple[int, str, any]],
                      errors: list[str] = None) -> None:
    """
    Add an entry to the LDAP store.

    :param entry_dn: the entry DN
    :param mod_entry: the list of modified entry attributes
    :param errors: incidental error messages
    """
    # obtain the LDAP client object
    conn: LDAPObject = ldap_init(errors=errors)

    if conn:
        if not isinstance(errors, list):
            errors = []
        # bind the LDAP client with the LDAP server
        bound: bool = ldap_bind(errors=errors,
                                ldap_client=conn)
        if not errors:
            try:
                conn.modify_s(dn=entry_dn,
                              modlist=mod_entry)
            except Exception as e:
                errors.append(f"Error on the LDAP modify entry operation: {__ldap_except_msg(e)}")

        # unbind the LDAP client
        if bound:
            ldap_unbind(errors=errors,
                        ldap_client=conn)


def ldap_delete_entry(entry_dn: str,
                      errors: list[str] = None) -> None:
    """
    Remove an entry to the LDAP store.

    :param entry_dn: the entry DN
    :param errors: incidental error messages
    """
    # obtain the LDAP client object
    conn: LDAPObject = ldap_init(errors=errors)

    if conn:
        if not isinstance(errors, list):
            errors = []
        # bind the LDAP client with the LDAP server
        bound: bool = ldap_bind(errors=errors,
                                ldap_client=conn)
        if not errors:
            try:
                conn.delete_s(dn=entry_dn)
            except Exception as e:
                errors.append(f"Error on the LDAP delete entry operation: {__ldap_except_msg(e)}")

        # unbind the LDAP client
        if bound:
            ldap_unbind(errors=errors,
                        ldap_client=conn)


def ldap_modify_user(user_id: str,
                     attrs: list[tuple[str, bytes | None]],
                     errors: list[str] = None) -> None:
    """
    Modify a user entry at the LDAP store.

    :param user_id: id of the user
    :param attrs: the list of modified attributes
    :param errors: incidental error messages
    """
    # invoke the search operation
    search_data: list[tuple[str, dict]] = ldap_search(base_dn=f"cn=users,{LDAP_BASE_DN}",
                                                      attrs=[attr[0] for attr in attrs],
                                                      scope=ldap.SCOPE_ONELEVEL,
                                                      filter_str=f"cn={user_id}",
                                                      errors=errors)
    if not search_data:
        if not isinstance(errors, list):
            errors = []
        # the search operation did not return data, report the error
        errors.append(f"Error on the LDAP modify user operation: User '{user_id}' not found")

        if not errors:
            entry_dn: str = search_data[0][0]

            # build the modification list
            mod_entries: list[tuple[int, str, bytes | None]] = []
            for attr_name, new_value in attrs:
                entry_list: list[bytes] = search_data[0][1].get(attr_name)
                if new_value:
                    curr_value: bytes = None if entry_list is None else entry_list[0]
                    # assert whether the old and new values are equal
                    if new_value != curr_value:
                        # define the modification mode
                        if curr_value is None:
                            mode: int = ldap.MOD_ADD
                        else:
                            mode: int = ldap.MOD_REPLACE
                        mod_entries.append((mode, attr_name, new_value))
                elif entry_list:
                    mod_entries.append((ldap.MOD_DELETE, attr_name, None))

            # are there attributes to be modified ?
            if len(mod_entries) > 0:
                # yes, modify them
                ldap_modify_entry(entry_dn=entry_dn,
                                  mod_entry=mod_entries,
                                  errors=errors)


def ldap_change_pwd(user_dn: str,
                    new_pwd: str,
                    curr_pwd: str | None = None,
                    errors: list[str] = None) -> str:
    """
    Modify a user password at the LDAP store.

    :param user_dn: the user's DN credentials
    :param new_pwd: the new password
    :param curr_pwd: optional current password
    :param errors: incidental error messages
    """
    # initialize the return variable
    result: str | None = None

    # obtain the LDAP client object
    ldap_client: LDAPObject = ldap_init(errors=errors)

    # bind the LDAP client with the LDAP server, if obtained
    if ldap_client:
        if not isinstance(errors, list):
            errors = []
        if curr_pwd:
            # perform the bind with the DN provided
            bound: bool = ldap_bind(ldap_client=ldap_client,
                                    bind_dn=user_dn,
                                    bind_pwd=curr_pwd,
                                    errors=errors)
        else:
            # perform the standard bind
            bound: bool = ldap_bind(ldap_client=ldap_client,
                                    errors=errors)
        if not errors:
            try:
                # is the connection safe ?
                if __is_secure(ldap_client):
                    # yes, use the directive 'passwd_s'
                    resp: tuple[None, bytes] = ldap_client.passwd_s(user=user_dn,
                                                                    oldpw=curr_pwd,
                                                                    newpw=new_pwd,
                                                                    extract_newpw=True)
                    result = resp[1].decode()
                else:
                    # no, use the directive 'modify_s'
                    ldap_client.modify_s(dn=user_dn,
                                         modlist=[(ldap.MOD_REPLACE, "userpassword", new_pwd.encode())])
                    result = new_pwd
            except Exception as e:
                errors.append(f"Error on the LDAP password change operation: {__ldap_except_msg(e)}")

        # unbind the LDAP client
        if bound:
            ldap_unbind(ldap_client=ldap_client,
                        errors=errors)
    return result


def ldap_search(base_dn: str,
                attrs: list[str],
                scope: str = None,
                filter_str: str = None,
                attrs_only: bool = False,
                errors: list[str] = None) -> list[tuple[str, dict]]:
    """
    Perform a search operation on the LDAP store, and return its results.

    :param base_dn: the base DN
    :param attrs: attributes to search for
    :param scope: optional scope for the search operation
    :param filter_str: optional filter for the search operation
    :param attrs_only: whether to return the values of the attributes searched
    :param errors: incidental error messages
    :return:
    """
    # initialize the return variable
    result:  list[tuple[str, dict]] | None = None

    # obtain the LDAP client object
    conn: LDAPObject = ldap_init(errors=errors)

    if conn:
        if not isinstance(errors, list):
            errors = []
        # bind the LDAP client with the LDAP server
        bound:  bool = ldap_bind(ldap_client=conn,
                                 errors=errors)
        if not errors:
            # if 'attrs_only' is specified, the values for the attributes are not returned
            attr_vals: int = 1 if attrs_only else 0
            try:
                # perform the search operation
                result = conn.search_s(base=base_dn,
                                       scope=scope or ldap.SCOPE_BASE,
                                       filterstr=filter_str or "(objectClass=*)",
                                       attrlist=attrs,
                                       attrsonly=attr_vals)
            except Exception as e:
                errors.append(f"Error on the LDAP search operation: {__ldap_except_msg(e)}")

        # unbind the LDAP client
        if bound:
            ldap_unbind(errors=errors,
                        ldap_client=conn)
    return result


def ldap_get_value(entry_dn: str,
                   attr: str,
                   errors: list[str] = None) -> bytes:
    """
    Retrieve the value of an attribute at the LDAP store.

    :param entry_dn: the DN entry
    :param attr: target attribute
    :param errors: incidental error messages
    :return: the target attribute's value
    """
    data: list[bytes] = ldap_get_value_list(entry_dn=entry_dn,
                                            attr=attr,
                                            errors=errors)
    return data[0] if isinstance(data, list) and len(data) > 0 else None


def ldap_add_value(entry_dn: str,
                   attr: str,
                   value: bytes,
                   errors: list[str] = None) -> None:
    """
    Add a value to an attribute at the LDAP store.

    :param entry_dn: the DN entry
    :param attr: target attribute
    :param value: value to add to the target attribute
    :param errors: incidental error messages
    :return: the target attribute's value
    """
    mod_entries: list[tuple[int, str, bytes]] = [(ldap.MOD_ADD, attr, value)]
    ldap_modify_entry(entry_dn=entry_dn,
                      mod_entry=mod_entries,
                      errors=errors)


def ldap_set_value(entry_dn: str,
                   attr: str,
                   value: bytes | None,
                   errors: list[str] = None) -> None:
    """
    Add a value to an attribute at the LDAP store.

    :param entry_dn: the DN entry
    :param attr: target attribute
    :param value: value to add to the target attribute
    :param errors: incidental error messages
    :return: the target attribute's value
    """
    if not isinstance(errors, list):
        errors = []

    # obtain the target attribute's current value
    curr_value: bytes = ldap_get_value(entry_dn=entry_dn,
                                       attr=attr,
                                       errors=errors)
    if not errors:
        # determine the modification mode
        mode: int | None = None
        if curr_value is None:
            if value is not None:
                mode = ldap.MOD_ADD
        elif value is None:
            mode = ldap.MOD_DELETE
        elif curr_value != value:
            mode = ldap.MOD_REPLACE

        if mode is not None:
            # update the LDAP store
            mod_entries: list[tuple[int, str, bytes]] = [(mode, attr, value)]
            ldap_modify_entry(entry_dn=entry_dn,
                              mod_entry=mod_entries,
                              errors=errors)


def ldap_get_value_list(entry_dn: str,
                        attr: str,
                        errors: list[str] = None) -> list[bytes]:
    """
    Retrieve the list of values of attribute *attr* in the LDAP store.

    :param entry_dn: the DN of the target entry
    :param attr: the target attribute
    :param errors: incidental error messages
    :return: the target attribute's list of values
    """
    # initialize the return variable
    result: list[bytes] | None = None

    # perform the search operation
    search_data: list[tuple[str, dict]] = ldap_search(base_dn=entry_dn,
                                                      attrs=[attr],
                                                      errors=errors)
    # did the search operation return data ?
    if isinstance(search_data, list) and len(search_data) > 0:
        # yes, proceed
        user_data: dict = search_data[0][1]
        result = user_data.get(attr)

    return result


def ldap_get_values(entry_dn: str,
                    attrs: list[str],
                    errors: list[str] = None) -> tuple[bytes, ...]:
    """
    Retrieve the values of attributes *attrs* in the LDAP store.

    :param entry_dn: the DN of the target entry
    :param attrs: the list of target attributes
    :param errors: incidental error messages
    :return: the values for the target attributes
    """
    # initialize the return variable
    result: tuple[bytes, ...] | None = None

    # perform the search operation
    search_data: tuple = ldap_get_values_lists(entry_dn=entry_dn,
                                               attrs=attrs,
                                               errors=errors)
    # did the search operation return data ?
    if isinstance(search_data, tuple):
        # yes, proceed
        search_items: list[bytes] = [item if item is None else item[0] for item in search_data]
        result = tuple(search_items)

    return result


def ldap_get_values_lists(entry_dn: str,
                          attrs: list[str],
                          errors: list[str]) -> tuple[list[bytes], ...]:
    """
    Retrieve the lists of values of attributes *attrs* in the LDAP store.

    :param entry_dn: the DN of the target entry
    :param attrs: the list of target attributes
    :param errors: incidental error messages
    :return: the target attributes' lists of values
    """
    # initialize the return variable
    result: tuple[list[bytes], ...] | None = None

    # perform the search operation
    search_data: list[tuple[str, dict]] = ldap_search(base_dn=entry_dn,
                                                      attrs=attrs,
                                                      errors=errors)
    if search_data:
        user_data: dict = search_data[0][1]
        items: list[list[bytes]] = [user_data.get(attr) for attr in attrs]
        result = tuple(items)

    return result


def __is_secure(conn: LDAPObject) -> bool:

    # noinspection PyProtectedMember
    return conn._uri.startswith("ldaps:") # noqa SLF001


def __ldap_except_msg(exc: Exception) -> str:

    if isinstance(exc, ldap.LDAPError):
        err_data: any = exc.args[0]
        # type(exc) -> <class '<class-name'>
        cls: str = f"{type(exc)}"[8:-2]
        result: str = f"'Type: {cls}; Code: {err_data.get('result')}; Msg: {err_data.get('desc')}'"
        info: str = err_data.get("info")
        if info:
            result = f"{result[:-1]}; Info: {info}'"
    else:
        result: str = exc_format(exc=exc,
                                 exc_info=sys.exc_info())
    return result
