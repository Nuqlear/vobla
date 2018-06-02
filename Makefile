.PHONY: build test run down shell


build:
	docker-compose -f docker-compose.yml -f docker-compose.build.yml build

test:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml up --exit-code-from backend

up:
	docker-compose -f docker-compose.yml -f docker-compose.build.yml -f docker-compose.dev.yml up -d --build

down:
	docker-compose -f docker-compose.yml -f docker-compose.build.yml -f docker-compose.dev.yml down

shell:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec backend env $(cat .env | xargs) bash
