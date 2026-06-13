docker compose run --rm -v ./scripts:/app/scripts web python /app/scripts/make_fixtures_script.py

    docker compose run --rm -v ./scripts:/app/scripts web python /app/scripts/load_recommendations.py