from flask import Flask, render_template_string, request, jsonify
import requests
import csv
import os
import json

app = Flask(__name__)


# =====================================
# Cargar datos desde data/nodes.csv
# =====================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "nodes.csv")

NODES = []


if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(
        f"No se encontró el archivo: {CSV_PATH}"
    )


with open(CSV_PATH, encoding="utf-8-sig") as f:

    reader = csv.DictReader(f)

    for row in reader:

        NODES.append({

            "label": row["Label"].strip(),

            "lat": float(row["Latitud"]),

            "lon": float(row["Longitud"]),

            "tipo": row["tipo organizacion"].strip()

        })



# =====================================
# HTML + CSS + JavaScript
# =====================================

HTML = """

<!DOCTYPE html>

<html>

<head>

<meta charset="utf-8">

<title>Mapa Región de Los Lagos</title>


<link rel="stylesheet"
href="https://unpkg.com/leaflet/dist/leaflet.css">


<style>


body {

    margin:0;

    font-family:Arial;

}


#map {

    height:100vh;

}



#search {

    position:absolute;

    top:10px;

    left:50px;

    z-index:1000;

    background:white;

    padding:10px;

    border-radius:5px;

    box-shadow:0 0 5px #777;

}



input {

    width:250px;

    padding:8px;

}


button {

    padding:8px;

}



.org-icon {

    text-align:center;

    font-size:32px;

}


</style>


</head>



<body>



<div id="search">


<input id="city" placeholder="Buscar ciudad">


<button onclick="buscar()">Buscar</button>


</div>



<div id="map"></div>



<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>



<script>


const map = L.map('map')

.setView([-41.7,-72.5],7);





L.tileLayer(

'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',

{

    attribution:'OpenStreetMap'

}

).addTo(map);





const iconos = {


    "Servicio":"🏠",

    "Comunitario":"👥",

    "Infancia":"🧒",

    "Judicial":"⚖️",

    "Salud":"✚",

    "Educacion":"📖",

    "Programa":"🔴",

    "programa":"🔴",

    "Gobierno local":"🏛️",

    "Espacio":"🌊",

    "Seguridad":"🚨",

    "Publico":"🏛️",

    "Público":"🏛️",

    "Privada":"🏢"


};





const nodos = {{nodes | safe}};





nodos.forEach(n => {



    let icon = L.divIcon({


        className:"org-icon",


        html: iconos[n.tipo],


        iconSize:[40,40],


        iconAnchor:[20,20]


    });





    L.marker(

        [n.lat,n.lon],

        {

            icon:icon

        }

    )

    .addTo(map)


    .bindPopup(

        `

        <b>${n.label}</b>

        <br>

        Tipo: ${n.tipo}

        `

    );


});







let searchMarker=null;



function buscar(){



    let ciudad=document.getElementById("city").value;



    fetch(

        "/buscar?q="+encodeURIComponent(ciudad)

    )


    .then(r=>r.json())


    .then(data=>{


        if(data.length===0){

            alert("No encontrado");

            return;

        }



        let lugar=data[0];



        let lat=parseFloat(lugar.lat);

        let lon=parseFloat(lugar.lon);



        map.setView(

            [lat,lon],

            12

        );




        if(searchMarker){

            map.removeLayer(searchMarker);

        }



        searchMarker=L.marker(

            [lat,lon]

        )

        .addTo(map)


        .bindPopup(

            lugar.display_name

        )

        .openPopup();



    });


}



</script>



</body>


</html>

"""



# =====================================
# Flask Routes
# =====================================


@app.route("/")

def index():

    return render_template_string(

        HTML,

        nodes=json.dumps(

            NODES,

            ensure_ascii=False

        )

    )




@app.route("/buscar")

def buscar():


    q=request.args.get("q","")



    response=requests.get(


        "https://nominatim.openstreetmap.org/search",


        params={


            "q":q+", Región de Los Lagos, Chile",


            "format":"json",


            "limit":5


        },


        headers={


            "User-Agent":"Flask-Leaflet-GIS-App"


        },


        timeout=10


    )



    return jsonify(response.json())





if __name__=="__main__":


    app.run(debug=True)