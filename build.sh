__GMAIL_PASSWORD="${GMAIL_PASSWORD:-not_set}"
__GMAIL_SENDER="${GMAIL_SENDER:-not_set}"
__GMAIL_RECEIVER="${GMAIL_RECEIVER:-not_set}"
__ENABLE_EMAIL="${ENABLE_EMAIL:-0}"
[ -z $@ ] && __TAG="latest" || __TAG=$1

docker build -t ordel_finder:${__TAG} \
    --build-arg GMAIL_PASSWORD=${__GMAIL_PASSWORD} \
    --build-arg GMAIL_SENDER=${__GMAIL_SENDER} \
    --build-arg GMAIL_RECEIVER=${__GMAIL_RECEIVER} \
    --build-arg ENABLE_EMAIL=${__ENABLE_EMAIL} \
    .
