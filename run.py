from flaskblog import app

# This Condition is only true if we run the module directly because at that time the name would be the
# name of our module. But if we import it to another module and then run it the name would be of that
# module and hence it will not run. This can be used to create modules that can be run as well as imported

if __name__ == '__main__':
    app.run(debug=True)

# Packaging helps solve the issue of circular imports. If we want to avoid it we can put everything
# in one file, but that is not good coding practice. Thus we use packaging.
# For more about circular imports watch Corey Schafer's 5th video of Flask Tutorials


# *********************Blue Prints***********************
# To learn this watch corey schafer's video on blue prints. For Dad's website we will do it at the
# end.
'''
We will learn how to use flask blue prints. We will move the configuration variables into their
own file and move the creation of teh application into its own function.
The benefits of doing this is that we can make our application to be more modular
Moving the creation of our application to a function will enable us to create multiple instances
of the app which can be used in production and testing. This is called an application factory.

We create the following packages/folders to differentiate the functionalities of each of them
1) user
2) posts
3) main - contains routes which are general in nature like home etc.

To tell python that the folder is a package we need to create a __init__.py file and it need not
contain anything.
'''
