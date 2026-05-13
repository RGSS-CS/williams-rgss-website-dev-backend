# williams-rgss-website-backend
The baseline for both websites provided to RGSS and Dr. GW Williams for the backend and frontend


## Setup

1. Run: 
    - `cp ./backend/backend/settings_dev.py ./backend/backend/settings_local.py` on development branch
    - `cp ./backend/backend/settings_prod.py ./backend/backend/settings_local.py` on PROD

Please be sure that you run `python manage.py makemigrations` and `python manage.py migrate` before starting the dev server
