#!/bin/bash

zip -r propel_slackbot.zip *.py
aws lambda update-function-code --function-name propel-slackbot --zip-file fileb://propel_slackbot.zip --region "us-east-1"
rm propel_slackbot.zip
