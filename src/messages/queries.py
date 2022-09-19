"""Houses all the queries for the sqlite database."""

TOTAL_DISTINCT_CONVO_QUERY = """
SELECT
    COUNT(*)
FROM
    chat;
"""

### Total count grouped
TOTAL_COUNT_WITHOUT_CONTACT_QUERY = """
SELECT
    chat.chat_identifier,
    count(chat.chat_identifier) AS message_count
FROM
    chat
JOIN chat_message_join
    ON chat.ROWID = chat_message_join.chat_id
JOIN message 
    ON chat_message_join.message_id = message.ROWID
GROUP BY
    chat.chat_identifier
ORDER BY
    message_count DESC;
"""


TOTAL_COUNT_WITH_CONTACT_QUERY = """
SELECT
    chat.chat_identifier,
    count(chat.chat_identifier) AS message_count,
    IFNULL(adb_record.ZFIRSTNAME, 'N/A') || ' ' || IFNULL(adb_record.ZLASTNAME, 'N/A')
FROM
    chat
JOIN chat_message_join
    ON chat.ROWID = chat_message_join.chat_id
JOIN message 
    ON chat_message_join.message_id = message.ROWID     
LEFT JOIN adb.ZABCDPHONENUMBER adb_phone
    ON chat.chat_identifier like '%' || replace(replace(replace(replace(adb_phone.ZFULLNUMBER, ' ', ''), '+', ''), ')', ''), '(', '')
LEFT JOIN adb.ZABCDRECORD adb_record
    ON adb_phone.ZOWNER = adb_record.Z_PK
GROUP BY
    chat.chat_identifier, adb_record.ZFIRSTNAME || ' ' || adb_record.ZLASTNAME
ORDER BY
    message_count DESC;
"""

ALL_CONTACT_BY_NAME = """
SELECT
    chat.chat_identifier,
    IFNULL(adb_record.ZFIRSTNAME, 'N/A') || ' ' || IFNULL(adb_record.ZLASTNAME, 'N/A') as fullname 
FROM
    chat
LEFT JOIN adb.ZABCDPHONENUMBER adb_phone
    ON chat.chat_identifier like '%' || replace(replace(replace(replace(adb_phone.ZFULLNUMBER, ' ', ''), '+', ''), ')', ''), '(', '')
LEFT JOIN adb.ZABCDRECORD adb_record
    ON adb_phone.ZOWNER = adb_record.Z_PK
WHERE 1=1
AND chat.chat_identifier not like 'chat%'
AND LENGTH(chat.chat_identifier) != 5
GROUP BY 
    chat.chat_identifier, fullname
ORDER BY
    fullname asc;
"""
# exclude the groupchats above

### All messages
ALL_MESSAGES_BY_DATE = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
ORDER BY
    message_date ASC;
"""

ALL_MESSAGES_WITH_CONTACT_BY_DATE = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier,
    IFNULL(adb_record.ZFIRSTNAME, 'N/A') || ' ' || IFNULL(adb_record.ZLASTNAME, 'N/A')
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
LEFT JOIN adb.ZABCDPHONENUMBER adb_phone
    ON chat.chat_identifier like '%' || replace(replace(replace(replace(adb_phone.ZFULLNUMBER, ' ', ''), '+', ''), ')', ''), '(', '')
LEFT JOIN adb.ZABCDRECORD adb_record
    ON adb_phone.ZOWNER = adb_record.Z_PK
ORDER BY
    message_date ASC
"""

### Search logic
SEARCH_BY_TEXT_WITH_CONTACT = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier,
    IFNULL(adb_record.ZFIRSTNAME, 'N/A') || ' ' || IFNULL(adb_record.ZLASTNAME, 'N/A')
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
LEFT JOIN adb.ZABCDPHONENUMBER adb_phone
    ON chat.chat_identifier like '%' || replace(replace(replace(replace(adb_phone.ZFULLNUMBER, ' ', ''), '+', ''), ')', ''), '(', '')
LEFT JOIN adb.ZABCDRECORD adb_record
    ON adb_phone.ZOWNER = adb_record.Z_PK
WHERE
    message.text like '%{search_text}%'
ORDER BY
    message_date ASC;
"""

SEARCH_BY_TEXT_WITHOUT_CONTACT = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
WHERE
    message.text like '%{search_text}%'
ORDER BY
    message_date ASC;
"""

SEARCH_BY_TEXT_AND_NUMBER_WITH_CONTACT = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier,
    IFNULL(adb_record.ZFIRSTNAME, 'N/A') || ' ' || IFNULL(adb_record.ZLASTNAME, 'N/A')
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
LEFT JOIN adb.ZABCDPHONENUMBER adb_phone
    ON chat.chat_identifier like '%' || replace(replace(replace(replace(adb_phone.ZFULLNUMBER, ' ', ''), '+', ''), ')', ''), '(', '')
LEFT JOIN adb.ZABCDRECORD adb_record
    ON adb_phone.ZOWNER = adb_record.Z_PK
WHERE
    message.text like '%{search_text}%'
    and chat.chat_identifier like '%{search_number}'
ORDER BY
    message_date ASC;
"""

SEARCH_BY_TEXT_AND_NUMBER_WITHOUT_CONTACT = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
WHERE
    message.text like '%{search_text}%'
    and chat.chat_identifier like '%{search_number}'
ORDER BY
    message_date ASC;
"""

SEARCH_BY_TEXT_AND_NAME_WITH_CONTACT = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier,
    IFNULL(adb_record.ZFIRSTNAME, 'N/A') || ' ' || IFNULL(adb_record.ZLASTNAME, 'N/A')
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
LEFT JOIN adb.ZABCDPHONENUMBER adb_phone
    ON chat.chat_identifier like '%' || replace(replace(replace(replace(adb_phone.ZFULLNUMBER, ' ', ''), '+', ''), ')', ''), '(', '')
LEFT JOIN adb.ZABCDRECORD adb_record
    ON adb_phone.ZOWNER = adb_record.Z_PK
WHERE
    message.text like '%{search_text}%'
    and IFNULL(adb_record.ZFIRSTNAME, 'N/A') || ' ' || IFNULL(adb_record.ZLASTNAME, 'N/A') like '%{search_name}%'
ORDER BY
    message_date ASC;
"""

### Get By Name Logic
GET_BY_NUMBER_WITH_CONTACT = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier,
    IFNULL(adb_record.ZFIRSTNAME, 'N/A') || ' ' || IFNULL(adb_record.ZLASTNAME, 'N/A')
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
LEFT JOIN adb.ZABCDPHONENUMBER adb_phone
    ON chat.chat_identifier like '%' || replace(replace(replace(replace(adb_phone.ZFULLNUMBER, ' ', ''), '+', ''), ')', ''), '(', '')
LEFT JOIN adb.ZABCDRECORD adb_record
    ON adb_phone.ZOWNER = adb_record.Z_PK
WHERE
    chat.chat_identifier like '%{get_number}'
ORDER BY
    message_date ASC;
"""

GET_BY_NUMBER_WITHOUT_CONTACT = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
WHERE
    chat.chat_identifier like '%{get_number}'
ORDER BY
    message_date ASC;
"""

GET_BY_NAME_AND_DATE_WITH_CONTACT = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier,
    IFNULL(adb_record.ZFIRSTNAME, 'N/A') || ' ' || IFNULL(adb_record.ZLASTNAME, 'N/A')
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
LEFT JOIN adb.ZABCDPHONENUMBER adb_phone
    ON chat.chat_identifier like '%' || replace(replace(replace(replace(adb_phone.ZFULLNUMBER, ' ', ''), '+', ''), ')', ''), '(', '')
LEFT JOIN adb.ZABCDRECORD adb_record
    ON adb_phone.ZOWNER = adb_record.Z_PK
WHERE
    IFNULL(adb_record.ZFIRSTNAME, 'N/A') || ' ' || IFNULL(adb_record.ZLASTNAME, 'N/A') like '%{get_name}%'
AND
    date(message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") = '{get_date}'
ORDER BY
    message_date ASC;
"""

GET_BY_NUMBER_AND_DATE_WITH_CONTACT = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier,
    IFNULL(adb_record.ZFIRSTNAME, 'N/A') || ' ' || IFNULL(adb_record.ZLASTNAME, 'N/A')
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
LEFT JOIN adb.ZABCDPHONENUMBER adb_phone
    ON chat.chat_identifier like '%' || replace(replace(replace(replace(adb_phone.ZFULLNUMBER, ' ', ''), '+', ''), ')', ''), '(', '')
LEFT JOIN adb.ZABCDRECORD adb_record
    ON adb_phone.ZOWNER = adb_record.Z_PK
WHERE
    chat.chat_identifier like '%{get_number}'
AND
    date(message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") = '{get_date}'
ORDER BY
    message_date ASC;
"""

GET_BY_NUMBER_AND_DATE_WITHOUT_CONTACT = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
WHERE
    chat.chat_identifier like '%{get_number}'
AND
    date(message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") = '{get_date}'
ORDER BY
    message_date ASC;
"""

GET_BY_DATE_WITH_CONTACT = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier,
    IFNULL(adb_record.ZFIRSTNAME, 'N/A') || ' ' || IFNULL(adb_record.ZLASTNAME, 'N/A')
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
LEFT JOIN adb.ZABCDPHONENUMBER adb_phone
    ON chat.chat_identifier like '%' || replace(replace(replace(replace(adb_phone.ZFULLNUMBER, ' ', ''), '+', ''), ')', ''), '(', '')
LEFT JOIN adb.ZABCDRECORD adb_record
    ON adb_phone.ZOWNER = adb_record.Z_PK
WHERE
    date(message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") = '{get_date}'
ORDER BY
    message_date ASC;
"""

GET_BY_DATE_WITHOUT_CONTACT = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
WHERE
    date(message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") = '{get_date}'
ORDER BY
    message_date ASC;
"""


GET_BY_NAME_WITH_CONTACT = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier,
    IFNULL(adb_record.ZFIRSTNAME, 'N/A') || ' ' || IFNULL(adb_record.ZLASTNAME, 'N/A')
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
LEFT JOIN adb.ZABCDPHONENUMBER adb_phone
    ON chat.chat_identifier like '%' || replace(replace(replace(replace(adb_phone.ZFULLNUMBER, ' ', ''), '+', ''), ')', ''), '(', '')
LEFT JOIN adb.ZABCDRECORD adb_record
    ON adb_phone.ZOWNER = adb_record.Z_PK
WHERE
    IFNULL(adb_record.ZFIRSTNAME, 'N/A') || ' ' || IFNULL(adb_record.ZLASTNAME, 'N/A') like '%{get_name}%'
ORDER BY
    message_date ASC;
"""

### Generate logic
AGGREGATE_MESSAGES_BY_NUMBER_WITH_CONTACT = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier,
    IFNULL(adb_record.ZFIRSTNAME, 'N/A') || ' ' || IFNULL(adb_record.ZLASTNAME, 'N/A')
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
LEFT JOIN adb.ZABCDPHONENUMBER adb_phone
    ON chat.chat_identifier like '%' || replace(replace(replace(replace(adb_phone.ZFULLNUMBER, ' ', ''), '+', ''), ')', ''), '(', '')
LEFT JOIN adb.ZABCDRECORD adb_record
    ON adb_phone.ZOWNER = adb_record.Z_PK
WHERE
    chat.chat_identifier like '%{search_number}'
ORDER BY
    message_date ASC;
"""

AGGREGATE_MESSAGES_BY_NUMBER_WITHOUT_CONTACT = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
WHERE
    chat.chat_identifier like '%{search_number}'
ORDER BY
    message_date ASC;
"""


AGGREGATE_MESSAGES_BY_NAME_WITH_CONTACT = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    GROUP_CONCAT(message.text, ". "),
    message.is_from_me,
    chat.chat_identifier,
    IFNULL(adb_record.ZFIRSTNAME, 'N/A') || ' ' || IFNULL(adb_record.ZLASTNAME, 'N/A')
FROM
    chat
JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message. "ROWID"
LEFT JOIN adb.ZABCDPHONENUMBER adb_phone
    ON chat.chat_identifier like '%' || replace(replace(replace(replace(adb_phone.ZFULLNUMBER, ' ', ''), '+', ''), ')', ''), '(', '')
LEFT JOIN adb.ZABCDRECORD adb_record
    ON adb_phone.ZOWNER = adb_record.Z_PK
WHERE
    IFNULL(adb_record.ZFIRSTNAME, 'N/A') || ' ' || IFNULL(adb_record.ZLASTNAME, 'N/A') like '%{search_name}%'
ORDER BY
    message_date ASC;
"""

if __name__ == "__main__":
    print(
        """
    Here's what you should run from the command line (if you're on a mac):
    $ sqlite3 /Users/$USER/Library/Messages/chat.db
    sqlite> attach "/Users/$USER/Library/Application Support/AddressBook/AddressBook-v22.abcddb" as adb;  # note, you should actually put the value of $USER
    """
    )
