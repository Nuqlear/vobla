docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec vobla-api-service env $(cat .env | xargs) bash
