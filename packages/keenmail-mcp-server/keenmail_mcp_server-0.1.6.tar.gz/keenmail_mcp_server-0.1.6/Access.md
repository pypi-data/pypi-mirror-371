curl --location 'https://app.keenmail.com/api/v1/emails/sendTemplate?apiKey=dd60bff2349a149afb77c33072bf877e9b32b4c3c5c0bc6118e3a6823947019d&secret=ae9dba2dbb8e348224daf33e74749893bca9649be03afc036f7610cf38c74487' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
--data-raw '{
    "templateId": "awsdemofollowupemail",
    "providerId": "amazonaws",
    "recipients": [
        {
            "from": "ai@optimoz.com",
            "to": "renesa@optimoz.com",
            "cc": [],
            "bcc": [],
            "data": {}
        }
    ]
}'