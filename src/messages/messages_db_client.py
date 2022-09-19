"""This file is to handle the database <-> client interactions.
It handles all of the sqlite3 connections."""

import os
import sqlite3

from typing import Any, List, Optional, cast

from datetime import datetime

from messages.queries import (
    ALL_CONTACT_BY_NAME,
    GET_BY_DATE_WITH_CONTACT,
    GET_BY_DATE_WITHOUT_CONTACT,
    GET_BY_NAME_AND_DATE_WITH_CONTACT,
    GET_BY_NUMBER_AND_DATE_WITH_CONTACT,
    GET_BY_NUMBER_AND_DATE_WITHOUT_CONTACT,
    TOTAL_DISTINCT_CONVO_QUERY,
    TOTAL_COUNT_WITHOUT_CONTACT_QUERY,
    TOTAL_COUNT_WITH_CONTACT_QUERY,
    ALL_MESSAGES_BY_DATE,
    ALL_MESSAGES_WITH_CONTACT_BY_DATE,
    SEARCH_BY_TEXT_WITH_CONTACT,
    SEARCH_BY_TEXT_WITHOUT_CONTACT,
    SEARCH_BY_TEXT_AND_NUMBER_WITH_CONTACT,
    SEARCH_BY_TEXT_AND_NUMBER_WITHOUT_CONTACT,
    SEARCH_BY_TEXT_AND_NAME_WITH_CONTACT,
    GET_BY_NUMBER_WITH_CONTACT,
    GET_BY_NUMBER_WITHOUT_CONTACT,
    GET_BY_NAME_WITH_CONTACT,
)


class MessagesDbClient:
    """
    Notes on chat.db database schema.

    sqlite> .tables
    _SqliteDatabaseProperties
    kvtable
    attachment - metadata and storage location
    message - all messages sent and received
    chat - a collection of your messages (both direct and group)
    message_attachment_join - join table
    chat_handle_join - join table
    message_processing_task -
    chat_message_join
    sync_deleted_attachments
    deleted_messages
    sync_deleted_chats
    handle - metadata about chats
    sync_deleted_messages
    """

    # Default messages sqlite3 path
    MESSAGE_DB_PATH = os.path.expanduser("~") + "/Library/Messages/chat.db"
    # Best guess for AddressBook parent path
    ADDRESS_BOOK_DB_PARENT_PATH = (
        os.path.expanduser("~") + "/Library/Application Support/AddressBook"
    )

    def __init__(self) -> None:
        if not os.access(self.MESSAGE_DB_PATH, os.R_OK):
            raise OSError(
                f"Do not have access to the MESSAGE_DB_PATH {self.MESSAGE_DB_PATH}. "
                "Please check permissions and ensure read access"
            )
        self.conn = sqlite3.connect(self.MESSAGE_DB_PATH)
        cursor = self.conn.cursor()
        max_adb_file = self._get_address_book_filename()
        self._cached_does_edb_table_exist: Optional[bool] = None
        try:
            cursor.execute("ATTACH ? AS adb;", [max_adb_file])
            self.conn.commit()
        except Exception as ex:
            print(f"Exception {ex}")
        finally:
            cursor.close()

    def total_distinct_convos(self) -> int:
        """Returns the number of distinct iMessage conversations"""
        return cast(int, self._run_independent_query(TOTAL_DISTINCT_CONVO_QUERY)[0][0])

    def total_messages_by_contact_or_number_sorted(
        self, limit_number: Optional[int] = None
    ) -> List[Any]:
        """Returns the total number of messages per each contact"""
        return self._run_query_with_adb_if_avail(
            TOTAL_COUNT_WITH_CONTACT_QUERY,
            TOTAL_COUNT_WITHOUT_CONTACT_QUERY,
            limit_number,
        )

    def all_contacts(self) -> List[Any]:
        """Gets all contacts the user has texted."""
        return self._run_independent_query(ALL_CONTACT_BY_NAME)

    def all_messages_sorted(self, limit_number: Optional[int] = None) -> List[Any]:
        """Returns all messages sorted based in chronological order.
        This will be an expensive underlying query."""
        return self._run_query_with_adb_if_avail(
            ALL_MESSAGES_WITH_CONTACT_BY_DATE, ALL_MESSAGES_BY_DATE, limit_number
        )

    def search_messages_by_text(
        self,
        search_text: str,
        search_number: Optional[str] = None,
        search_name: Optional[str] = None,
        search_date: Optional[datetime] = None,
        limit_number: Optional[int] = None,
        before_number: Optional[int] = None,
        after_number: Optional[int] = None,
    ) -> List[Any]:
        """Returns all message content filtered on a certain string.
        If you choose to pass in a phone number or a name, we will search on that as well"""
        if search_name is not None and search_number is not None:
            raise ValueError(
                f"Both search_name {search_name} and search_number \
                {search_number} are not allowed to be specified."
            )

        if search_number is not None:
            return self._run_query_with_adb_if_avail(
                SEARCH_BY_TEXT_AND_NUMBER_WITH_CONTACT.format(
                    search_text=search_text, search_number=search_number
                ),
                SEARCH_BY_TEXT_AND_NUMBER_WITHOUT_CONTACT.format(
                    search_text=search_text, search_number=search_number
                ),
                limit_number,
            )

        if search_name is not None:
            return self._run_independent_query(
                SEARCH_BY_TEXT_AND_NAME_WITH_CONTACT.format(
                    search_text=search_text, search_name=search_name
                ),
                limit_number,
            )

        return self._run_query_with_adb_if_avail(
            SEARCH_BY_TEXT_WITH_CONTACT.format(search_text=search_text),
            SEARCH_BY_TEXT_WITHOUT_CONTACT.format(search_text=search_text),
            limit_number,
        )

    def get_messages(
        self,
        get_number: Optional[str] = None,
        get_name: Optional[str] = None,
        get_date: Optional[datetime] = None,
        limit_number: Optional[int] = None,
    ) -> List[Any]:
        """Dumps all messages for a given name or number."""
        if get_number is None and get_name is None and get_date is None:
            raise ValueError(
                "Both get_number and get_name cannot be None at the same time."
            )

        if get_number and get_name:
            raise ValueError(
                "Both get_number and get_name cannot be specified at the same time."
            )

        if get_date and (get_name or get_number):
            converted_date = get_date.strftime("%Y-%m-%d")
            if get_name:
                return self._run_independent_query(
                    GET_BY_NAME_AND_DATE_WITH_CONTACT.format(
                        get_name=get_name,
                        get_date=converted_date,
                    ),
                    limit_number,
                )

            if get_number:
                return self._run_query_with_adb_if_avail(
                    GET_BY_NUMBER_AND_DATE_WITH_CONTACT.format(
                        get_number=get_number, get_date=converted_date
                    ),
                    GET_BY_NUMBER_AND_DATE_WITHOUT_CONTACT.format(
                        get_number=get_number, get_date=converted_date
                    ),
                    limit_number,
                )

            return self._run_query_with_adb_if_avail(
                GET_BY_DATE_WITH_CONTACT.format(get_date=converted_date),
                GET_BY_DATE_WITHOUT_CONTACT.format(get_date=converted_date),
                limit_number,
            )

        if get_name and self._does_adb_table_exists():
            return self._run_independent_query(
                GET_BY_NAME_WITH_CONTACT.format(get_name=get_name), limit_number
            )

        if get_number:
            return self._run_query_with_adb_if_avail(
                GET_BY_NUMBER_WITH_CONTACT.format(get_number=get_number),
                GET_BY_NUMBER_WITHOUT_CONTACT.format(get_number=get_number),
                limit_number,
            )

        return []

    ### Private Methods ###
    def _run_independent_query(
        self, query: str, limit_number: Optional[int] = None
    ) -> List[Any]:
        if limit_number:
            query = query.replace(";\n", f"\nLIMIT {limit_number};\n")
        cursor = self.conn.cursor()
        return cursor.execute(query).fetchall()

    def _run_query_with_adb_if_avail(
        self,
        with_contact_query: str,
        without_contact_query: str,
        limit_number: Optional[int] = None,
    ) -> List[Any]:
        if limit_number:
            with_contact_query = with_contact_query.replace(
                ";\n", f"\nLIMIT {limit_number};\n"
            )
            without_contact_query = without_contact_query.replace(
                ";\n", f"\nLIMIT {limit_number};\n"
            )

        cursor = self.conn.cursor()
        if self._does_adb_table_exists():
            data = cursor.execute(with_contact_query).fetchall()
        else:
            data = cursor.execute(without_contact_query).fetchall()
        return data

    # Address Book methods
    def _get_address_book_filename(self) -> str:
        """Gets the maximum address book file, which we will then assume
        to be the corresponding sqlite db file for referencing ContactInfo."""
        tgt_path = self.ADDRESS_BOOK_DB_PARENT_PATH
        address_book_files = [
            os.path.join(tgt_path, f)
            for f in os.listdir(tgt_path)
            if os.path.isfile(os.path.join(tgt_path, f))
        ]
        max_file = max(address_book_files, key=lambda x: os.stat(x).st_size)
        return max_file

    def _does_adb_table_exists(self) -> bool:
        """Ensures that we have the needed table for getting the true contact name"""
        if self._cached_does_edb_table_exist is not None:
            return self._cached_does_edb_table_exist

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM adb.ZABCDPHONENUMBER LIMIT 1").fetchall()
        except Exception as _:
            self._cached_does_edb_table_exist = False
            return False
        self._cached_does_edb_table_exist = True
        return True


if __name__ == "__main__":
    client = MessagesDbClient()
    print(client.search_messages_by_text("absolute stud"))
    print(client.total_messages_by_contact_or_number_sorted())
    # print(x.total_messages_by_contact())
