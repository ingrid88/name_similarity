import flask
from flask import request
import numpy as np
import pandas as pd
import os

#---------- Rank Names ----------------#
fuzzynames = pd.read_csv("similarnames.data")

def similar_sounding_names(name):
    ks = fuzzynames[fuzzynames.name==name].values[0]
    ranked_names = fuzzynames[(fuzzynames.soundex == ks[5])
                    & (fuzzynames.phonetics == ks[3])
                    & (fuzzynames.meta1 == ks[4])].sort_values(by='count',ascending=False)[['name','count']]
    return ranked_names.iloc[0:8]

#---------- Generate Json / Calculate distances ----------------#

import distance
def build_json(df):
    node_list = []
    edge_list = []
    name_list = list(df.name)
    for name in name_list:
        node_list.append({'name': name})
    for i in range(0,len(name_list)):
        for j in range(i,len(name_list)):
            d = distance.levenshtein(name_list[i],name_list[j])
            if d < 3 and j!=i:
                edge_list.append({'source':i,'target':j,'value':d+1})
    n = {'nodes': node_list, 'edges': edge_list}
    return n


#---------- URLS AND WEB PAGES -------------#

# Initialize the app
app = flask.Flask(__name__)

# Homepage
@app.route("/")
def viz_page():
    """
    Homepage: serve our visualization page, awesome.html
    """
    with open("index.html", 'r') as viz_file:
        return viz_file.read()

@app.route("/names", methods=['POST'])
def names():
    """
    Take the imputed name and search for similar ones, return json
    object that encodes for edges(name similarity) and nodes(names)
    """
    data = flask.request.json
    name = data["example"]
    r = similar_sounding_names(name)
    results = build_json(r)

    return flask.jsonify(results)

#--------- RUN WEB APP SERVER ------------#

# Start the app server on port 80
# (The default website port)
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=80)
