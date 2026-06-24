from flask import Flask, render_template_string, request, jsonify, send_file
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

GEOJSON_PATH = os.path.join(
    BASE_DIR,
    "mapaficticio.geojson"
)

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

.comuna-label{

    background:transparent !important;

    border:none !important;

    box-shadow:none !important;

    color:#222;

    font-weight:bold;

    font-size:12px;

    text-shadow:
        1px 1px 2px white,
       -1px -1px 2px white;
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


const map = L.map('map');

const nodos = {{nodes | safe}};

const colores = {

    "Programa":"#ff69b4",
    "programa":"#ff69b4",

    "Salud":"#4CAF50",

    "Judicial":"#6ec6ff",
    "judicial":"#6ec6ff",

    "Educacion":"#ffd54f",

    "Comunitario":"#ff9800",

    "Seguridad":"#ff8a80",

    "Gobierno local":"#7fffd4",

    "Infancia":"#c7a17a",

    "Publico":"#c2185b",
    "Público":"#c2185b",

    "Privada":"#556b2f",

    "Servicio":"#000000"

};

const nombresFicticios = {

    "Puerto Montt":"Puerto Verde",
    "Puerto Varas":"Lago Claro",
    "Frutillar":"Bosque Azul",
    "Llanquihue":"Villa Horizonte",
    "Los Muermos":"Campo Norte",
    "Maullín":"Bahía Serena",
    "Calbuco":"Isla Bruma",
    "Cochamó":"Valle Neblina",
    "Fresia":"Campos del Sur",
    "Puerto Octay":"Río Cristal",

    "Osorno":"Valle Central",
    "Purranque":"Río Dorado",
    "Puyehue":"Monte Claro",
    "Río Negro":"Bosque del Norte",
    "San Pablo":"Campo Azul",

    "Ancud":"Puerto Bruma",
    "Castro":"Villa Estrella",
    "Chonchi":"Lago del Sur",
    "Curaco de Vélez":"Isla Serena",
    "Dalcahue":"Puerto Niebla",
    "Puqueldón":"Isla Horizonte",
    "Queilén":"Bahía Clara",
    "Quellón":"Puerto Austral",
    "Quemchi":"Bosque Marino",
    "Quinchao":"Isla del Sol",

    "Hualaihué":"Costa Verde",
    "Palena":"Valle Austral",
    "Futaleufú":"Río Celeste",
    "Chaitén":"Puerto del Viento"
};

fetch("/mapa")
.then(r => r.json())
.then(data => {

    const capaMapa = L.geoJSON(data, {

        style: {

            color:"#666",
            weight:1,

            fillColor:"#7a8f62",
            fillOpacity:0.9

        },

        onEachFeature:function(feature, layer){

            const nombreReal =
                feature.properties.Comuna;

            const nombreFicticio =
                nombresFicticios[nombreReal]
                || nombreReal;

            layer.bindTooltip(
                nombreFicticio,
                {
                    permanent:true,
                    direction:"center",
                    className:"comuna-label"
                }
            );

        }

    }).addTo(map);

    map.fitBounds(
        capaMapa.getBounds()
    );

});

nodos.forEach(n => {

    let color =
        colores[n.tipo] || "#888888";

    L.circleMarker(
        [n.lat,n.lon],
        {
            radius:7,

            fillColor:color,

            color:"#ffffff",

            weight:1,

            opacity:1,

            fillOpacity:0.95
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

let searchMarker = null;

function buscar(){

    let ciudad =
        document.getElementById("city").value;

    fetch(
        "/buscar?q=" +
        encodeURIComponent(ciudad)
    )

    .then(r => r.json())

    .then(data => {

        if(data.length===0){

            alert("No encontrado");

            return;
        }

        let lugar=data[0];

        let lat=parseFloat(lugar.lat);
        let lon=parseFloat(lugar.lon);

        map.setView([lat,lon],12);

        if(searchMarker){

            map.removeLayer(
                searchMarker
            );
        }

        searchMarker=L.marker([lat,lon])

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


@app.route("/mapa")
def mapa():

    return send_file(
        GEOJSON_PATH,
        mimetype="application/json"
    )


if __name__=="__main__":


    app.run(debug=True)