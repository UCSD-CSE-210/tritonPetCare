Libraries required: flask (installed by pip), sqlite3 (default in Mac)


Commands:
All following commands are executed in the root path of the application.

Export variables:
>>export FLASK_APP=PetCare/run.py
>>export FLASK_DEBUG=1

Initialize database (required if and only if the shcema is changed):
>>flask initdb

Run application:
>>flask run

Access database:
>>sqlite3 PetCare/PetCare.db