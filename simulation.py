#!python3
import urllib.request
from io import StringIO
import csv
import argparse
import datetime
from pythonds.basic.queue import Queue


# class server and request
class Server:
    def __init__(self):

        self.currentTask = None
        self.timeRemaining = 0

    def tick(self):
        if self.currentTask is not None:
            self.timeRemaining = self.timeRemaining - 1
            if self.timeRemaining <= 0:
                self.currentTask = None

    def busy(self):
        if self.currentTask is not None:
            return True
        else:
            return False

    def startNext(self, newtask):
        self.currentTask = newtask
        self.timeRemaining = newtask.getTime()


class Request:
    def __init__(self, data):
        self.pages = None
        self.timestamp = int(data[0])
        self.timetaken = int(data[2])

    def getStamp(self):
        return self.timestamp

    def getPages(self):
        return self.pages

    def getTime(self):
        return self.timetaken

    def waitTime(self, currenttime):
        return currenttime - self.timestamp


def main():
    """download the contents"""

    # Initializing parser
    commandParser = argparse.ArgumentParser(description="Send a ­­url parameter to the script")
    # add the parameter's for file
    commandParser.add_argument("--file", type=str, help="Link to the csv file")
    # add the parameter's for server's
    commandParser.add_argument("--servers", type=int, help="Link to the csv file")
    # parse the argument's
    args = commandParser.parse_args()
    # if url is not given
    if not args.file:
        exit()
    if not args.servers:
        simulateOneServer(args.file)
    else:  # else simulate multiple servers function
        simulateManyServers(args.file, args.servers)


def simulateOneServer(file):
    """function to handle requests using one server"""

    global averageWait
    content = urllib.request.urlopen(file).read().decode("ascii", "ignore")  # fetch contents
    data = StringIO(content)
    # read csv file
    csv_reader = csv.reader(data, delimiter=',')

    dataList = []  # store data from csv

    for line in csv_reader:
        # Use list to store data
        dataList.append(line)

    requestQueue = Queue()  # queue tor requests
    waitingtimes = []  # list to store's that are  waiting before a request is processed
    server = Server()  # instantiate server class
    # listlength=len(dataList)-1
    for i in dataList:
        # iterated the requests
        request = Request(i)  # pass data to request class
        requestQueue.enqueue(request)  # enqueue the request object
        if (not requestQueue.isEmpty()) and (not server.busy()):  # if server is not busy and queue is not empty
            nexttask = requestQueue.dequeue()  # dequeue first item in queue
            waitingtimes.append(nexttask.waitTime(int(i[0])))  # append to waiting time to list
            server.startNext(nexttask)  # if server is free move to the next task
        server.tick()  # server timer
        averageWait = sum(waitingtimes) / len(waitingtimes)  # calculate average wait time
        print("Average Wait %6.2f secs %3d tasks remaining." % (
            averageWait, requestQueue.size()))  # similar to pritning example in notes

    print("Average latency is {} seconds".format(averageWait))
    return averageWait  # return latency


def simulateManyServers(file, noOfServers):
    global averageWait
    content = urllib.request.urlopen(file).read().decode("ascii", "ignore")  # fetch contents
    data = StringIO(content)
    # read csv file
    csv_reader = csv.reader(data, delimiter=',')

    dataList = []  # store data from csv
    for line in csv_reader:
        # Use list to store data
        dataList.append(line)

    requestQueue = Queue()  # queue for requests
    waitingtimes = []  # array to store waiting time
    servers = [Server() for a in range(noOfServers)]  # create the number of server objects passed as parameter
    # eg if 2 then two servers will be instantiated

    for i in dataList:
        # iterate the data list
        request = Request(i)  # create a request object
        requestQueue.enqueue(request)  # add object to queue

        for server in servers:  # iterate the servers
            if (not server.busy()) and (
                    not requestQueue.isEmpty()):
                nexttask = requestQueue.dequeue()
                waitingtimes.append(nexttask.waitTime(int(i[0])))  # append waiting time to list
                server.startNext(nexttask)  # start new task
            server.tick()  # server ticker
        averageWait = sum(waitingtimes) / len(waitingtimes)
        print("Average Wait %6.2f secs %3d tasks remaining." % (averageWait, requestQueue.size()))

    print("Average latency is {} seconds".format(averageWait))
    return averageWait  # return average latency


# Call main function when script runs
if __name__ == "__main__":
    main()
