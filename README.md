# How to set-up
It's meant to be run on Heroku.

To run locally

# Requirements:
    * A PostgreSQL Database, which can be easily created in Heroku.
        * In this project, I decided that the tools description and other information will be stored there, although it's completely
        based on testing and playing with SQLAlchemy. For the scope of current project, it honestly would be easier to store it in a file or even hard code it, but I thought this might be neat when trying to expand the base of available tools in future.
    * An authorization URL. This can be optained from Google Cloud Console.
    * Redis URL to it's DB, which also can be created in Heroku.