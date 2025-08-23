curl -X 'POST' \                                                                  ✔  at 10:06:41 
  'https://app.keenmail.com/api/v1/emails/sendTemplate?apiKey=dd60bff2349a149afb77c33072bf877e9b32b4c3c5c0bc6118e3a6823947019d&secret=ae9dba2dbb8e348224daf33e74749893bca9649be03afc036f7610cf38c74487' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "templateId": "awsdemofollowupemail",
  "providerId": "amazonaws",
  "recipients": [
    {
      "from": "mcp@optimoz.com",
      "to": "renesa@optimoz.com",
      "cc": [
      ],
      "bcc": [
      ],
      "data": {
      }
    }
  ]
}'