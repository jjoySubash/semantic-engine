indexMapping = {
    "properties": {
        "Title": {
            "type":'text'
        },
        "Genre": {
            "type":"text"
        },
        "Description": {
            "type":"text"
        },
        "Director": {
            "type":"text"
        },
        "Actors": {
            "type":"text"
        },
        "Year": {
            "type":"long"
        },
        "Runtime (Minutes)": {
          "type":"long"  
        },
        "Rating":{
            "type":"long"
        },
        "Votes":{
            "type":"long"
        },
        "Revenue (Millions)":{
            "type":"long"
        },
        "Metascore":{
            "type":"long"
        },
        "Embedding":{
            "type": "dense_vector",
            "dims": 768,
            "index": True,
            "similarity": "l2_norm"
        }
    }
}