# williams-rgss-website-backend
The baseline for both websites provided to RGSS and Dr. GW Williams for the backend and frontend


## Setup

1. Run: 
    - `cp ./backend/backend/settings_dev.py ./backend/backend/settings_local.py` on development branch
    - `cp ./backend/backend/settings_prod.py ./backend/backend/settings_local.py` on PROD

Please be sure that you run `python manage.py makemigrations` and `python manage.py migrate` before starting the dev server

## Development test data

From `backend/`, run `python manage.py generate_testdata --club-amount 10 --seed demo`.
This adds clubs with categories and announcements, and updates
site, council, ticker, page, and social-media settings. Text respects model limits.
Use `--skip-settings` to keep existing settings or `--skip-clubs` to update settings
only. Image files and connection/CAPTCHA settings are preserved. A repeated seed
reproduces randomized values on a fresh database; existing club names must be unique.

Run the test suite from `backend/` with `python manage.py test`.
