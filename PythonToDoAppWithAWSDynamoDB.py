# Programmer - python_scripts (Abhijith Warrier)

# PYTHON GUI FOR ADDING TO-DO ITEMS TO AWS DynamoDB TABLE & DELETING COMPLETED ITEMS FROM TABLE

# Amazon DynamoDB is a fully managed NoSQL database service that provides fast and predictable
# performance with seamless scalability.
# Boto3 makes it easy to integrate our Python application, library, or script with
# AWS services including Amazon S3, Amazon EC2, Amazon DynamoDB, and more.
#
# DynamoDB Table Configuration:
# Create a DynamoDB table in AWS with a name of your choice and item_id as Partition Key.
#
# The module can be installed using the command - pip install boto3

# Importing necessary packages
import boto3
import uuid
import tkinter as tk
from tkinter import *

# Defining CreateWidgets() function to create necessary tkinter widgets
def CreateWidgets():
    toDoItemLabel = Label(root, text="NEW ITEM: ", bg="deepskyblue4")
    toDoItemLabel.grid(row=0, column=0, padx=5, pady=5)
    root.toDoItemEntry = Entry(root, width=30, bg='snow3', textvariable=toDoItem)
    root.toDoItemEntry.grid(row=0, column=1, padx=5, pady=5)
    root.toDoItemEntry.config(foreground="black")

    addItemButton = Button(root, text="ADD ITEM", command=addToDoItem)
    addItemButton.grid(row=0, column=2, padx=5, pady=5)

    toDoItemsListLabel = Label(root, text="ToDo LIST:", bg="deepskyblue4")
    toDoItemsListLabel.grid(row=3, column=0, padx=5, pady=5)
    root.toDoItemsListBox = Listbox(root, width=55, height=20, bg='snow3')
    root.toDoItemsListBox.grid(row=4, column=0, rowspan=12, columnspan=3, padx=5, pady=5)
    # Binding onItemSelect() event to the ListBox Widget
    root.toDoItemsListBox.bind('<<ListboxSelect>>', onItemSelect)
    root.toDoItemsListBox.config(foreground="black")

    doneItemLabel = Label(root, text="DONE ITEM: ", bg="deepskyblue4")
    doneItemLabel.grid(row=19, column=0, padx=5, pady=5)
    root.doneItemEntry = Entry(root, width=30, bg='snow3', textvariable=completedItem)
    root.doneItemEntry.grid(row=19, column=1, padx=5, pady=5)
    root.doneItemEntry.config(foreground="black")

    downloadButton = Button(root, text="MARK DONE", command=markItemAsDone)
    downloadButton.grid(row=19, column=2, padx=5, pady=15)

    root.notificationLabel = Label(root, bg="deepskyblue4", font="'' 20")
    root.notificationLabel.grid(row=20, column=0, padx=5, pady=5, columnspan=3)

    # Calling configureAWSSession() function on application start
    configureAWSSession()

# Defining configureAWSSession() function to create AWS Session
def configureAWSSession():
    # Declaring global variables
    global dynamodbTableName, dynamodbClient, dynamodbResource, dynamodbObject
    # Storing the AWS DynamoDB Table name
    dynamodbTableName = "<YOUR_DYNAMODB_TABLE_NAME>"
    # Creating AWS session using the boto3 library
    awsSession = boto3.session.Session(profile_name="<YOUR_AWS_PROFILE>", region_name="<YOUR_AWS_REGION>")
    # Creating S3 access object using the session
    dynamodbClient = awsSession.client("dynamodb")
    # Creating S3 Resource Object using the session
    dynamodbResource = awsSession.resource("dynamodb")
    # Creating an object of S3 Bucket
    dynamodbObject = dynamodbResource.Table(dynamodbTableName)
    # Calling the listToDoItems() to list all to-do items at application startup
    listToDoItems()

# Defining listToDoItems() to list all the to-do items that are present in DynamoDB table
def listToDoItems():
    # Creating global variable and setting it to an empty list
    global toDoItemsIdList
    toDoItemsIdList = []
    # Clearing the list widget and list before displaying the updated list
    root.toDoItemsListBox.delete(0, END)
    # Clearing the list before updating the to-do item list
    toDoItemsList = []
    # Scanning the dynamodb table and fetching all the records from the table
    dynamodbResponse = dynamodbObject.scan()
    dynamodbTableItems = dynamodbResponse["Items"]
    # Looping through each item in the response and adding them to the toDoItemsList list
    for item in dynamodbTableItems:
        toDoItemsList.append(item)
        toDoItemsIdList.append(item["item_id"])
    # Looping through the toDoItemsList and displaying item in ListBox using insert() method
    for item in dynamodbTableItems:
        root.toDoItemsListBox.insert("end", item["item_name"])

# Defining addToDoItem() function to add user-input item to the to-do list and display it in the ListBox
def addToDoItem():
    # Fetching the user-selected to-do item from the widget using get() of tkinter variable
    newToDoItem = toDoItem.get()
    # Generating unique id for the new to-do item and storing it in a variable
    newToDoItemId = uuid.uuid4()
    # Adding the new to-do item to the dynamodb table using put_item() function of DynamoDB Client
    try:
        # Parameters - item_id, item_name
        dynamodbResponse = dynamodbClient.put_item(
            TableName = dynamodbTableName,
            Item={
                "item_id": {"S": str(newToDoItemId)},
                "item_name": {"S": newToDoItem}
            }
        )
        # Checking if the response of put_item() function was successful
        if dynamodbResponse['ResponseMetadata']['HTTPStatusCode']==200:
            # Displaying success notification
            root.notificationLabel.config(text="New To-Do Item Added Successfully!", foreground="green2")
            # Clearing the item entry widget
            root.toDoItemEntry.delete(0, END)
            listToDoItems()
    except Exception as e:
        # Displaying error notification
        root.notificationLabel.config(text="Error While Adding To-Do Item!", foreground="red4")

# Defining onItemSelect() to display the ListBox Cursor Selection in the Entry widget
def onItemSelect(evt):
    # Creating global variable to store the id of the selected item from the list
    global selectedItemId
    selectedItemId = toDoItemsIdList[root.toDoItemsListBox.curselection()[0]]
    # Fetching the ListBox cursor selection and storing the id of the selected item
    selectedItem = root.toDoItemsListBox.get(root.toDoItemsListBox.curselection())
    # Displaying the selected text from ListBox in the widget using tkinter variable
    completedItem.set(selectedItem)

# Defining markItemAsDone() function to mark the selected item as COMPLETED
def markItemAsDone():
    # Fetching and storing the user-selected item id from the global variable selectedItemId
    completedItemId = selectedItemId
    try:
        # Querying the DynamoDB table for the selected item using it's id and deleting the item
        dynamodbResponse = dynamodbObject.delete_item(
            Key={
                "item_id": completedItemId
            }
        )
        # Checking if the response of put_item() function was successful
        if dynamodbResponse['ResponseMetadata']['HTTPStatusCode']==200:
            # Displaying success notification
            root.notificationLabel.config(text="Item Removed From The Table List!", foreground="green2")
            # Clearing the item entry widget
            root.doneItemEntry.delete(0, END)
            listToDoItems()
    except Exception as e:
        # Displaying error notification
        root.notificationLabel.config(text="Error While Marking Item As Done!", foreground="red4")

# Creating object of tk class
root = tk.Tk()

# Setting the title, background color, windowsize &
# disabling the resizing property
root.title("PythonToDoAppWithDynamoDB")
root.config(background="deepskyblue4")
root.resizable(False, False)

# Creating the tkinter variables
toDoItem = StringVar()
completedItem = StringVar()
# Creating an empty list
toDoItemsList = []

# Calling the CreateWidgets() function
CreateWidgets()

# Defining infinite loop to run application
root.mainloop()
