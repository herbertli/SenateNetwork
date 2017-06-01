import json

INFINITY = 1e9


def convert_votes_to_adjacency(data):
    """
    Converts voting data into an adjacency matrix
    :param data: initial vote data, see vdata.json
    :type data: Dictionary
    :return: adjacency matrix, key: senator, value: dictionary showing connections to other senators
    :rtype: Dictionary
    """
    adj_matrix = {}
    for name in data:
        adj_matrix[name] = {}
        for other_name in data[name]:
            adj_matrix[name][other_name] = int(data[name][other_name]) / int(data[name][name])
    return adj_matrix


def convert_money_to_adjacency(data):
    """
    Converts campaign donation data into an adjacency matrix
    :param data: initial campaign donation data, see mdata.json
    :type data: Dictionary
    :return: adjacency matrix, key: senator, value: dictionary showing connections to other senators
    :rtype: Dictionary
    """
    new_data = {}

    industries = data.keys()
    for industry in industries:
        senators = data[industry].keys()
        for senator in senators:
            if senator not in new_data:
                new_data[senator] = {}
            for other_senator in senators:
                if other_senator not in new_data[senator]:
                    new_data[senator][other_senator] = 1
                else:
                    new_data[senator][other_senator] += 1

    adj_matrix = {}
    for name in new_data:
        adj_matrix[name] = {}
        for other_name in new_data[name]:
            adj_matrix[name][other_name] = int(new_data[name][other_name]) / int(new_data[name][name])
    return adj_matrix


def get_diameter(distances):
    """
    Get diameter of a network/graph
    :param distances: distances matrix, distance[i][j] is the distance from senator i to senator j
    :type distances: Dictionary
    :return: diameter
    :rtype: int
    """
    max_dist = 0
    for i in distances:
        for j in distances:
            if distances[i][j] != INFINITY:
                max_dist = max(max_dist, distances[i][j])
    return max_dist


def get_average_distance(distances):
    """
    Get average distance of a network/graph
    :param distances: distances matrix, distance[i][j] is the distance from senator i to senator j
    :type distances: Dictionary
    :return: average distance
    :rtype: int
    """
    total = 0
    counter = 0
    for i in distances:
        for j in distances:
            if distances[i][j] != INFINITY:
                total += distances[i][j]
                counter += 1
    return total / counter


def floyd_warshall(adj_matrix, threshold):
    """
    Finds all pairs shortest path
    :param adj_matrix: adjacency matrix
    :type adj_matrix: Dictionary
    :param threshold: percentage cutoff
    :type threshold: float
    :return: distances matrix
    :rtype: Dictionary
    """
    senators = list(adj_matrix.keys())
    distances = {}

    for i in senators:
        distances[i] = {}
        for j in senators:
            distances[i][j] = INFINITY

    for i in senators:
        adj_matrix[i][i] = 0

    for i in adj_matrix:
        for j in adj_matrix[i]:
            if adj_matrix[i][j] >= threshold:
                distances[i][j] = 1

    for k in distances:
        for i in distances:
            for j in distances:
                if distances[i][j] > distances[i][k] + distances[k][j]:
                    distances[i][j] = distances[i][k] + distances[k][j]

    return distances


def get_components(adj_matrix, threshold):
    """
    Count components of a graph
    :param adj_matrix: adjacency matrix
    :type adj_matrix: Dictionary
    :param threshold: percentage threshold
    :type threshold: float
    :return: number of components
    :rtype: int
    """
    visited = []
    components = 0

    for name in adj_matrix:
        if name not in visited:
            components += 1
            visited = dfs(visited, adj_matrix, threshold, name)

    return components


def dfs(visited, adj_matrix, threshold, name):
    """
    Depth first search
    :param visited: list containing visited nodes
    :type visited: List
    :param adj_matrix: adjacency matrix
    :type adj_matrix: Dictionary
    :param threshold: percentage threshold
    :type threshold: float
    :param name: current node
    :type name: String
    :return: new visited list
    :rtype: List
    """
    visited.append(name)
    for other_name in adj_matrix[name]:
        if adj_matrix[name][other_name] >= threshold and other_name not in visited:
            visited = dfs(visited, adj_matrix, threshold, other_name)
    return visited


def get_stats(adj_matrix, threshold):
    distances = floyd_warshall(adj_matrix, threshold)
    diameter = get_diameter(distances)
    average = get_average_distance(distances)
    components = get_components(adj_matrix, threshold)
    print("Threshold:", threshold)
    print("Average distance is", average)
    print("Diameter of graph is", diameter)
    print("Number of components is", components)
    print()
    return True


if __name__ == "__main__":

    filename = input("(v)oting data, or (m)oney data: ")
    if filename == "v":
        with open("vdata.json", "r") as f:
            data = json.load(f)
            data = convert_votes_to_adjacency(data)
            while True:
                threshold = input("Enter threshold (enter 50 for 50%), or (q)uit: ")
                if threshold == "q":
                    break
                else:
                    get_stats(data, float(threshold) / 100)
    elif filename == "m":
        with open("mdata.json", "r") as f:
            data = json.load(f)
            data = convert_money_to_adjacency(data)
            while True:
                threshold = input("Enter threshold (enter 50 for 50%), or (q)uit: ")
                if threshold == "q":
                    break
                else:
                    get_stats(data, float(threshold) / 100)
    else:
        print("Invalid option (case sensitive)")
