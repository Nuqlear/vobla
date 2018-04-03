docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec backend env $(cat .env | xargs) bash
