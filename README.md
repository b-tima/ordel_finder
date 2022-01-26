# ordel_finder

Ordel finder is a python script that attempts to crack the ordel.se word of the day. It does this by going through all the five letter words in the swedish dictionary and reads the response from the ordel.se API.

https://ordel.se/

## Setup

```
# Install dependencies
pipenv install --dev

# Add your email to the .env file
echo "GMAIL={GMAIL}" >> ".env"
echo "GMAIL_PASSWORD={GMAIL}" >> ".env"

# Enter the pipenv shell
pipenv shell

# Build and run the docker image
sh build.sh
docker run ordel_finder

```

## Credits
This package was created with Cookiecutter and the [sourcery-ai/python-best-practices-cookiecutter](https://github.com/sourcery-ai/python-best-practices-cookiecutter) project template.
