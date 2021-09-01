import operator
from termgraph.termgraph import chart

 
class gitactivity():
    def __init__(self, type):
        self.ipaddresses = {}
        self.repositories = {}
        self.users = {}
        self.type = type
        self.counter = 0

    def display_result(self, result, howMany, title, graph):
        print("==========================================")
        result = result[:howMany]
        print("Top {} {}".format(howMany, title))
        if graph:
            self.show_graph(result)
        else:
            self.show_list(result)
        top_total = sum([item[1] for item in result])
        print("These represent {:.2%} of total requests".format(top_total/self.counter))
        print(" ")

    def jira_result(self, result, howMany, title, graph):
        print("h2. ==========================================")
        result = result[:howMany]
        print("h3. Top {} {}".format(howMany, title))
        print("{noformat}")
        if graph:
            self.show_graph(result)
        else:
            self.show_list(result)
        print("{noformat}")
        top_total = sum([item[1] for item in result])
        print("These represent {:.2%} of total requests".format(top_total/self.counter))
        print(" ")

    def file_result(self, result, howMany, title, outputFile):
        pass

    def show_list(self, result):
        for key, value in result:
            print("{1:12,d} - {0:}".format(key, value))

    def show_graph(self, result):
        # defaults args
        args = {
            "width": 30,
            "format": "{:,d}",
            "suffix": "",
            "stacked": False,
            "no_labels": False,
            "vertical": False,
            "histogram": False,
            "no_values": False,
        }
        labels = [item[0] for item in result]
        data = [[item[1]] for item in result] # required to be a list of lists
        chart(labels=labels, data=data, args=args, colors=[])

    def display(self, howMany, output, outputFile, graph):
        print("h1. {}".format(self.type))
        print("h2. Total Requests: {0:8,d} ".format(self.counter))

        ip_result = sorted(self.ipaddresses.items(), key=operator.itemgetter(1), reverse=True)
        repo_result = sorted(self.repositories.items(), key=operator.itemgetter(1), reverse=True)
        user_result = sorted(self.users.items(), key=operator.itemgetter(1), reverse=True)

        if output == "screen":
            self.display_result(ip_result, howMany, "IP Addresses", graph)
            self.display_result(repo_result, howMany, "Repositories", graph)
            self.display_result(user_result, howMany, "Users", graph)
        elif output == "jira":
            self.jira_result(ip_result, howMany, "IP Addresses", graph)
            self.jira_result(repo_result, howMany, "Repositories", graph)
            self.jira_result(user_result, howMany, "Users", graph)
        else:
            self.file_result(ip_result, howMany, "IP Addresses", outputFile)
            self.file_result(repo_result, howMany, "Repositories", outputFile)
            self.file_result(user_result, howMany, "Users", outputFile)

    def add_entry(self, ip, repo, user):
        ipaddress = self.ipaddresses.setdefault(ip, 0)
        self.ipaddresses[ip] = ipaddress + 1
        repository = self.repositories.setdefault(repo, 0)
        self.repositories[repo] = repository + 1
        username = self.users.setdefault(user, 0)
        self.users[user] = username + 1
        self.counter += 1
