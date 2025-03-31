I want to create a login page that will say login with Microsoft and take us to the working login with azure. :complete

I also want a username and password box where we can login using a username and password: complete

We will need to create a database to store the credentials. I also know we'll create a model for it. I'll want to make sure it's using sqlachemy 2: Complete

I want to install cloud flare so I can control dns access: complete

I want to setup a way to manage access from routes

We will need to start breaking the code into seperate files.

I want the azure to check if they are a valid users prior to logging in, if not it will direct them to contact admin
I want to put the register link behind the application admin
I want to put another register link behind the web admin page
I need to think through multiple applications on the same framework
admin page needs to control the password requirements
admin can lock a user, users can never be deleted, they can be inactive or active
    I want to setup a condition where if they get their password wrong 10 times I lock their account and it can only be reactivated from the admin panel
create a provision page where users can be assigned access and row level security
I would think we want routes, fields and row level security. We want the options of hide, view, edit

after security is all the way done. I'm good to create the spreadsheets