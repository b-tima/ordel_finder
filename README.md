# ordel_finder

Ordel finder is a python script that attempts to crack the ordel.se word of the day. It does this by going through all the five letter words in the swedish dictionary and reads the response from the ordel.se API.

https://ordel.se/

## Setup

You need to have pipenv and docker installed on your system.

```
# Install dependencies
pipenv install --dev

# Enable email notifications of the word by typing the following commands:
echo "ENABLE_EMAIL=1" >> .env

# Add your email to the .env file
echo "GMAIL={GMAIL}" >> .env
echo "GMAIL_PASSWORD={GMAIL}" >> .env

# Enter the pipenv shell
pipenv shell

# Build and run the docker image (replace <tag> with whatever tag you want. if none is set, "latest" will be used)
sh build.sh <tag>
docker run ordel_finder

# If you run the debug image, you should instead write
docker run ordel_finder:debug

```

## Credits
This package was created with Cookiecutter and the [sourcery-ai/python-best-practices-cookiecutter](https://github.com/sourcery-ai/python-best-practices-cookiecutter) project template.
