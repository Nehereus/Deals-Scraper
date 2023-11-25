docker build -t scraper-image ./scraper
docker build -t frontend-image ./frontend
docker-compose restart
docker image prune
