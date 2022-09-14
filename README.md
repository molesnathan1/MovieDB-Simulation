# Movie Database Simulation

## Introduction
In this project, we created a database and a set of programs to interact with it. The purpose of the project was to simulate the database management system (PostgreSQL) responding to many simultaneous requests to an IMDB-esque database. The programs represented different users who chose to interact with the information in the database. The accuracy and responsiveness of the database were tested against a multi-threaded implementation of the programs.

## DB Organization
The PostgreSQL (psql) server had two databases: a ‘core’ IMDB database which was by design immutable and a default database which received the bulk of the interactions. The core database was loaded from csv files and its design was provided.

The default database has the following tables:
- Users: keeps track of the system’s unique end users.
- Review: represents a user’s review (ratings and analysis) of a movie ReviewComments- keeps track of all of the comments on each review ReviewCommentInvite- invitations from a reviewer to another user asking them to
make a comment on their review
- Survey: represents a user-created survey, which has a variable number of questions that are stored in the survey question table
- SurveyInvite: an invite from a survey maker to another user asking them to respond to their survey
- SurveyQuestion: represents a question with answer options which belongs to a specific survey
- SurveyQuestionResponse: keeps track of responses to survey questions 
- Interface: associates movies with their aggregate ratings in a mutable table 
- Verifier: tracks all inserts done to other tables throughout program execution by recording their timestamp and status (successfully inserted, not inserted, or inserted with incorrect data).

## Program Organization
Our suite of programs are made in python, using the psycopg library to connect to psql. The Setup.py program takes in the user inputs (number of threads to create, number of users that each thread will create, and the number of actions each user will take), sets up the log file, resets the default database, creates the specified number of threads, and makes a UserSpawner for each thread. The Setup program is also where the database username can be set prior to program execution.

The UserSpawner program makes a connection to the database, creates the specified number of users (each of random type) including by adding them to the Users table, and starts the appropriate user program.

The UserCritic, HiredCritic, and GeneralUser programs each represent one of the types of user. They each randomly choose one of a given set of actions. The number of actions input to Setup determines the number of action choices made. For UserCritic, these actions are to take a random survey, create a survey, review a movie, or respond to a request (either a comment or a survey request). A GeneralUser’s actions are to take a random survey or comment on a movie review. A HiredCritic can review a movie, create a survey, request a user comment on one of their reviews, request a user respond to one of their surveys, or comment on another user’s movie review. Note the HiredCritic.py file contains a few helper functions which are outside of the HiredCritic.HiredCritic class; these functions are used by various programs but are not considered part of the HiredCritic program. The actions that users can take map to the database tables, and each action requires some interaction with the default database. The semantic constraints enforced around these actions and interactions are discussed later.

The Verifier program is an intermediary between the other programs which create data and the database. It edits and checks every insert into the database except for those to its verifier table. It then selects that information back from the database and compares the expected values with the returned values. Therefore, the number of commands which are successfully inserted, not inserted, or inserted with incorrect data is tracked. The verifier table and log file hold the details about the data integrity.

The ResetDB program simply wipes the tables from the database, which removes all of the currently populated data. Similarly, the CreateDB program builds the database tables. These are each called once by Setup and are otherwise used as standalone programs.

## Semantic constraints enforced in the programs
#### Setup.py
To run the program three parameters, which act as constraints, are required: the number of threads, the number of users created per thread, and the number of actions each user does.

#### GeneralUser.py
General Users are constrained to commenting on reviews and answering surveys that they were requested to take. If there are no surveys that they were invited to complete then they must comment on a review.

#### HiredCritic.py
Hired Critics are constrained to requesting a user to take a survey, requesting a user to comment on a review, writing a comment on a review, creating a survey, and writing a review. Explanations of movie reviews are constrained to 6 pre-written strings that are chosen based on the random ratings out of 10 on particulars about the movie. Comments and questions are randomly selected from a list of pre-written strings. They also only invite another user to comment on their review or take their survey if they have written a review or created a survey, respectively.

#### UserCritic.py
User Critics are constrained to reviewing a movie, creating a survey, taking a survey, and responding to a comment or survey request. Explanations of movie reviews are constrained to 6 pre-written strings that are chosen based on the random ratings out of 10 on particulars about the movie. Comments and questions are randomly selected from a list of pre-written strings.

#### UserSpawner.py
A user will be exactly one of: Hired Critic, User Critic, or General User. Additionally, a username will be exactly 12 lowercase letters, randomly generated from the alphabet.

## Results/Conclusion
We found that having over three threads did not seem to have an effect on the system. From using 1-3 threads there were only slight improvements on runtime and minimal additional stress on postgres. We ran multiple tests with varying numbers of threads, users and useractions. Using three threads, we found postgres would use 100% of the cpu with around 50 users doing only about 10 actions each. If a lesser amount of users or actions per users were used, the stress on the server would generally be less than 100%. If a greater ratio of users and actions were used the system would still be at 100% and the runtime would be longer. The integrity of the databases is tracked the entire time the program is run and provides a summary of these statistics, as well as a log file with the specifics of each action. This allows for confirmation that the system is working correctly. Postgres made no errors despite any given parameters, it would just take longer the larger the dataset it was working with. The one exception to this is when trying to have more than 100 threads connect to Postgres at once, which it rejected. Otherwise, it consistently added data accurately.
