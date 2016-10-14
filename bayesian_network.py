import sys
import getopt
from decimal import Decimal

cmd_input = False
try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:h', ['input=', 'help'])
except getopt.GetoptError:
    print "Please enter -i <input file name>"
    sys.exit(2)

for opt, arg in opts:
    if opt in ('-h', '--help'):
        print "Please enter -i <input file name>"
        sys.exit(2)
    elif opt in ('-i', '--input'):
        in_file = arg.strip()
        if len(in_file) > 0:
            cmd_input = True
        else:
            cmd_input = False
    else:
        print "Please enter -i <input file name>"
        sys.exit(2)

if cmd_input == False:
    print "Please enter -i <input file name>"
    sys.exit(2)
    
#read input file and store the values
input_file = open(in_file, "r")

#read queries
PQ = []
EU = []
MEU = []
while True:
    input_line = input_file.readline().strip()
    if input_line == "******" :
        break
    if input_line[0] == "P":
        PQ.append(input_line)
    elif input_line[0:2] == "EU":
        EU.append(input_line)
    else:
        MEU.append(input_line)

#read probability distribution
lines = input_file.readlines()
nodes = []
node = []
values = {}
for line in lines:
    input_line = line.strip()
    if input_line == "***" or input_line == "******" :
        if values:
            node.append(values)
            values = {}
        nodes.append(node)
        node = []
        continue
    if input_line == "decision" :
        input_line = input_line.split(" ", 1)
        node.append(input_line)
    elif input_line[0].isalpha() :
        node.append(input_line)
    else:
        input_line = input_line.split(" ", 1)
        if len(input_line) == 1:
            node.append(input_line)
        else:
            key = input_line[1].replace(" ", "")
            values.update({key: input_line[0]})
if values:
    node.append(values)
nodes.append(node)

#seperate utility table
last_index = len(nodes) - 1
utility = []
if nodes[last_index][0].find("utility") != -1 :
    last_node = nodes.pop()
    utility_parent = last_node[0].split(" | ")[1]
    utility.append(utility_parent)
    utility.append(last_node[1])

#close input file
input_file.close()

#function to do summation over parent variables
def sumQuery(query, query_sign, parents, start_query):
    prob = 0
    if len(parents) == 1:
        parent_query = parents[0] + " = +"
        CP_query = query + " = " + query_sign + " | " + parent_query
        subprob = calculateCP(CP_query) * calculateJP(parent_query, start_query)
        prob += subprob
        parent_query = parents[0] + " = -"
        CP_query = query + " = " + query_sign + " | " + parent_query
        subprob = calculateCP(CP_query) * calculateJP(parent_query, start_query)
        prob += subprob
    if len(parents) == 2:
        for k in range(0,4):
            if k in [0, 1]:
                parent1_query = parents[0] + " = +, "
            else:
                parent1_query = parents[0] + " = -, "
            if k in [0, 2]:
                parent2_query = parents[1] + " = +"
            else:
                parent2_query = parents[1] + " = -"
            parent_query = parent1_query + parent2_query
            CP_query = query + " = " + query_sign + " | " + parent_query
            subprob = calculateCP(CP_query) * calculateJP(parent_query, start_query)
            prob += subprob
    if len(parents) == 3:
        for k in range(0,8):
            if k in [0, 1, 2, 3]:
                parent1_query = parents[0] + " = +, "
            else:
                parent1_query = parents[0] + " = -, "
            if k in [0, 1, 4, 5]:
                parent2_query = parents[1] + " = +, "
            else:
                parent2_query = parents[1] + " = -, "
            if k in [0, 2, 4, 6]:
                parent3_query = parents[2] + " = +"
            else:
                parent3_query = parents[2] + " = -"
            parent_query = parent1_query + parent2_query + parent3_query
            CP_query = query + " = " + query_sign + " | " + parent_query
            subprob = calculateCP(CP_query) * calculateJP(parent_query, start_query)
            prob += subprob
    return prob

#function to do summation over parent variables present in query
def sumQuery2(query, query_sign, parents, parents_signs, start_query):
    prob = 0
    if len(parents) == 1:
        parent_query = parents[0] + " = " + parents_signs[0]
        CP_query = query + " = " + query_sign + " | " + parent_query
        subprob = calculateCP(CP_query)
        prob += subprob
    if len(parents) == 2:
        count = 0
        for i in range(0, len(parents_signs)):
            if parents_signs[i] == "#" :
                count += 1
        if count == 0:
            parent1_query = parents[0] + " = " + parents_signs[0] + ", "
            parent2_query = parents[1] + " = " + parents_signs[1]
            parent_query = parent1_query + parent2_query
            CP_query = query + " = " + query_sign + " | " + parent_query
            subprob = calculateCP(CP_query)
            prob += subprob
        else:
            signs = "+-"
            for k in range(0, 2):
                parent_query = ""
                unknown_parent = ""
                for i in range(0, len(parents_signs)):
                    if parents_signs[i] == "#" :
                        parent_query += parents[i] + " = " + signs[k]
                        unknown_parent += parents[i] + " = " + signs[k]
                    else:
                        parent_query += parents[i] + " = " + parents_signs[i]
                    if i != len(parents_signs) - 1:
                        parent_query += ", "
                CP_query = query + " = " + query_sign + " | " + parent_query
                subprob = calculateCP(CP_query) * calculateJP(unknown_parent, start_query)
                prob += subprob
    if len(parents) == 3:
        count = 0
        for i in range(0, len(parents_signs)):
            if parents_signs[i] == "#" :
                count += 1
        if count == 0:
            parent1_query = parents[0] + " = " + parents_signs[0] + ", "
            parent2_query = parents[1] + " = " + parents_signs[1] + ", "
            parent3_query = parents[2] + " = " + parents_signs[2]
            parent_query = parent1_query + parent2_query + parent3_query
            CP_query = query + " = " + query_sign + " | " + parent_query
            subprob = calculateCP(CP_query)
            prob += subprob
        elif count == 1:
            signs = "+-"
            for k in range(0, 2):
                parent_query = ""
                unknown_parent = ""
                for i in range(0, len(parents_signs)):
                    if parents_signs[i] == "#" :
                        parent_query += parents[i] + " = " + signs[k]
                        unknown_parent += parents[i] + " = " + signs[k]
                    else:
                        parent_query += parents[i] + " = " + parents_signs[i]
                    if i != len(parents_signs) - 1:
                        parent_query += ", "
                CP_query = query + " = " + query_sign + " | " + parent_query
                subprob = calculateCP(CP_query) * calculateJP(unknown_parent, start_query)
                prob += subprob
        else:
            signs = "+++--+--"
            for k in range(0, 8, 2):
                parent_query = ""
                unknown_parent = ""
                unknowns = 2
                j = k
                for i in range(0, len(parents_signs)):
                    if parents_signs[i] == "#" :
                        parent_query += parents[i] + " = " + signs[j]
                        unknown_parent += parents[i] + " = " + signs[j]
                        unknowns -= 1
                        j += 1
                        if unknowns != 0:
                            unknown_parent += ", "
                    else:
                        parent_query += parents[i] + " = " + parents_signs[i]
                    if i != len(parents_signs) - 1:
                        parent_query += ", "
                CP_query = query + " = " + query_sign + " | " + parent_query
                subprob = calculateCP(CP_query) * calculateJP(unknown_parent, start_query)
                prob += subprob
            
    return prob

#function to lookup joint probability values in tables
def lookupJP(query, query_sign, start_query):
    for i in range(0, len(nodes)):
        if nodes[i][0] == query :
            if nodes[i][1][0] == "decision" :
                return Decimal(1)
            prob = Decimal(nodes[i][1][0])
            if query_sign == "-" :
                prob = Decimal(1) - prob
            return prob
        if nodes[i][0].find(query) != -1 :
            parent_array = nodes[i][0].split(" | ")[1]
            parents = parent_array.split()
            parents_in_query = False
            parents_signs = []
            for j in range(0, len(parents)):
                if start_query.find(parents[j]) != -1:
                    parents_in_query = True
                    sign_position = start_query.find(parents[j]) + len(parents[j]) + 3
                    start_query_sign = start_query[sign_position]
                    parents_signs.append(start_query_sign)
                else:
                    parents_signs.append("#")
            if parents_in_query == False :
                prob = sumQuery(query, query_sign, parents, start_query)
                return prob
            else:
                prob = sumQuery2(query, query_sign, parents, parents_signs, start_query)
                return prob

#function to calculate joint probabilities
def calculateJP(query, start_query):
    if query.find(",") == -1:
        query_array = query.split(" = ")
        prob = lookupJP(query_array[0], query_array[1], start_query)
        return prob
    else:
        prob = Decimal(1)
        query_array = query.split(", ")
        for i in range(0, len(query_array)):
            start_query = query
            prob = prob * calculateJP(query_array[i], start_query)
        return prob

#function to lookup conditional probability values in tables
def lookupCP(child_value, child_sign, parent_value, parent_sign):
    for i in range(0, len(nodes)):
        if nodes[i][0].find(" | ") != -1 :
            node = nodes[i][0].split(" | ")
            if child_value == node[0] and parent_value == node[1] :
                prob = Decimal(nodes[i][1][parent_sign])
                if child_sign == "-":
                    prob = Decimal(1) - prob
                return prob
    parents = parent_value.split()
    num_query = child_value + " = " + child_sign
    den_query = ""
    for j in range(0, len(parents)):
        num_query += ", " + parents[j] + " = " + parent_sign[j]
        if j == len(parents) - 1 :
            den_query += parents[j] + " = " + parent_sign[j]
        else:
            den_query += parents[j] + " = " + parent_sign[j] + ", "
    prob = calculateJP(num_query, "") / calculateJP(den_query, "")
    return prob

#function to calculate conditional probabilities
def calculateCP(query):
    query_array = query.split(" | ")
    event_array = query_array[0].split(", ")
    if len(event_array) == 1 :
        child = query_array[0].split(" = ")
        child_value = child[0]
        child_sign = child[1]
        parent_array = query_array[1].split(", ")
        parent_value = ""
        parent_sign = ""
        for i in range(0,len(parent_array)):
            parent = parent_array[i].split(" = ")
            parent_value = parent_value + parent[0] + " "
            parent_sign += parent[1]
        parent_value = parent_value.strip()
        prob = lookupCP(child_value, child_sign, parent_value, parent_sign)
        return prob
    else:
        new_query = query_array[0] + ", " + query_array[1]
        prob = calculateJP(new_query, "") / calculateJP(query_array[1], "")
        return prob

#function to calculate expected utility for joint probability
def calculateEUJP(query):
    utility_parents = utility[0].split(" ")
    parents_signs = []
    for j in range(0, len(utility_parents)):
        if query.find(utility_parents[j]) != -1:
            sign_position = query.find(utility_parents[j]) + len(utility_parents[j]) + 3
            parent_query_sign = query[sign_position]
            parents_signs.append(parent_query_sign)
        else:
            parents_signs.append("#")
    hash_count = 0
    for j in range(0, len(parents_signs)):
        if parents_signs[j] == "#" :
            hash_count += 1
    if hash_count == 1 :
        signs = "+-"
    elif hash_count == 2 :
        signs = "+++--+--"
    else:
        signs = "+++++-+-++---++-+---+---"
    loop_count = len(signs)/hash_count
    prob = 0
    n = 0
    for j in range(0, loop_count):
        subprob_query = ""
        utility_signs = ""
        for k in range(0, len(utility_parents)):
            if (parents_signs[k] == "#"):
                subprob_query += utility_parents[k] + " = " + signs[n] + ", "
                utility_signs += signs[n]
                n += 1
            else:
                utility_signs += parents_signs[k]
        subprob_query += query
        subprob = calculateJP(subprob_query, "") * Decimal(utility[1][utility_signs])
        prob += subprob
    return prob

#function to calculate expected utility for conditional probability
def calculateEUCP(query):
    query_items = query.split(" | ")
    new_query = query_items[1] + ", " + query_items[0]
    utility_parents = utility[0].split(" ")
    parents_signs = []
    for j in range(0, len(utility_parents)):
        if new_query.find(utility_parents[j]) != -1:
            sign_position = query.find(utility_parents[j]) + len(utility_parents[j]) + 3
            parent_query_sign = query[sign_position]
            parents_signs.append(parent_query_sign)
        else:
            parents_signs.append("#")
    hash_count = 0
    for j in range(0, len(parents_signs)):
        if parents_signs[j] == "#" :
            hash_count += 1
    if hash_count == 1 :
        signs = "+-"
    elif hash_count == 2 :
        signs = "+++--+--"
    else:
        signs = "+++++-+-++---++-+---+---"
    loop_count = len(signs)/hash_count
    prob = 0
    n = 0
    for j in range(0, loop_count):
        subprob_query = ""
        utility_signs = ""
        for k in range(0, len(utility_parents)):
            if (parents_signs[k] == "#"):
                subprob_query += utility_parents[k] + " = " + signs[n]
                utility_signs += signs[n]
                n += 1
            else:
                subprob_query += utility_parents[k] + " = " + parents_signs[k]
                utility_signs += parents_signs[k]
            if k == (len(utility_parents) - 1) :
                subprob_query += " | "
            else:
                subprob_query += ", "
        subprob_query += new_query
        subprob = calculateCP(subprob_query) * Decimal(utility[1][utility_signs])
        prob += subprob
    return prob

#function to calculate MEU for joint probabilities
def calculateMEUJP(query):
    query_array = query.split(", ")
    query_count = len(query_array)
    if query_count == 1 :
        signs = "+-"
    elif query_count == 2 :
        signs = "+++--+--"
    else:
        signs = "+++++-+-++---++-+---+---"
    loop_count = len(signs)/query_count
    max_EU = Decimal("-Infinity")
    n = 0
    for j in range(0, loop_count):
        subprob_query = ""
        utility_signs = ""
        for k in range(0, len(query_array)):
            subprob_query += query_array[k] + " = " + signs[n]
            utility_signs += signs[n]
            n += 1
            if k != (len(query_array)-1) :
                subprob_query += ", "
                utility_signs += " "
        subprob_EU = calculateEUJP(subprob_query)
        if subprob_EU > max_EU :
            max_EU = subprob_EU
            max_EU_signs = utility_signs
    print max_EU_signs, int(round(max_EU))
    output_file.write(str(max_EU_signs) + " ")
    output_file.write(str(int(round(max_EU))) + "\n")

#function to calculate MEU for conditional probabilities
def calculateMEUCP(query):
    query_array = query.split(" | ")
    event_array = query_array[0].split(", ")
    if len(event_array) == 1:
        signs = "+-"
        loop_count = 2
    else:
        signs = "+++--+--"
        loop_count = 4
    max_EU = Decimal("-Infinity")
    n = 0
    for j in range(0, loop_count):
        subprob_query = ""
        utility_signs = ""
        for k in range(0, len(event_array)):
            subprob_query += event_array[k] + " = " + signs[n] 
            utility_signs += signs[n]
            n += 1
        subprob_query += " | " + query_array[1]
        subprob_EU = calculateEUCP(subprob_query)
        if subprob_EU > max_EU :
            max_EU = subprob_EU
            max_EU_signs = utility_signs
    print max_EU_signs, int(round(max_EU))
    output_file.write(str(max_EU_signs) + " ")
    output_file.write(str(int(round(max_EU))) + "\n")

#create output file to print the inference
output_file = open("output.txt", "w")

#find probabilities for PQ queries
for i in range(0, len(PQ)):
    query = PQ[i][2:len(PQ[i])-1]
    if query.find(" | ") == -1 :
        prob = calculateJP(query, "")
        prob = Decimal(str(prob)).quantize(Decimal('.01'))
        print prob
        output_file.write(str(prob) + "\n")
    else:
        prob = calculateCP(query)
        prob = Decimal(str(prob)).quantize(Decimal('.01'))
        print prob
        output_file.write(str(prob) + "\n")
        
#find expected utility for EU queries
for i in range(0, len(EU)):
    query = EU[i][3:len(EU[i])-1]
    if query.find(" | ") == -1 :
        EU_value = calculateEUJP(query)
        EU_value = int(round(EU_value))
        print EU_value
        output_file.write(str(EU_value) + "\n")
    else:
        EU_value = calculateEUCP(query)
        EU_value = int(round(EU_value))
        print EU_value
        output_file.write(str(EU_value) + "\n")

#find maximum expected utility for MEU queries
for i in range(0, len(MEU)):
    query = MEU[i][4:len(MEU[i])-1]
    if query.find(" | ") == -1 :
        calculateMEUJP(query)
    else:
        calculateMEUCP(query)

#close output file
output_file.close()
