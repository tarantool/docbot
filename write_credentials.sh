#!/bin/bash
touch credentials.json

echo -e "{" > credentials.json
echo -e "\t\"GitHub\": {" >> credentials.json
echo -e "\t\t\"token\": \"${GITHUB_TOKEN}\"" >> credentials.json
echo -e "\t}\n}" >> credentials.json
