__GMAIL_PASSWORD="${GMAIL_PASSWORD:-not_set}"
__GMAIL_EMAIL="${GMAIL_EMAIL:-not_set}"
__ENABLE_EMAIL="${ENABLE_EMAIL:-0}"
if [ $# > 0 ]; then
    __TAG=$1
fi
if [ $# = 0 ]; then # I was unable use use else, dont know why
    __TAG="latest"
fi

docker build -t ordel_finder:${__TAG} \
    --build-arg GMAIL_PASSWORD=${__GMAIL_PASSWORD} \
    --build-arg GMAIL_EMAIL=${__GMAIL_EMAIL} \
    --build-arg ENABLE_EMAIL=${__ENABLE_EMAIL} \
    .
