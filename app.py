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

    background:white;

}


#map {

    height:100vh;

    background:white;

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

.comuna-label {

    background: transparent !important;

    border: none !important;

    box-shadow: none !important;

    color: white !important;

    font-size: 14px;

    font-weight: bold;

    text-align: center;

    white-space: nowrap;


    text-shadow:
        2px 2px 4px rgba(0,0,0,0.9),
        -1px -1px 3px rgba(0,0,0,0.9);

}

.legend {

    background:white;

    padding:10px;

    border-radius:8px;

    box-shadow:0 0 5px rgba(0,0,0,.3);

    line-height:18px;

    font-size:12px;

}

.legend span {

    display:inline-block;

    width:12px;

    height:12px;

    margin-right:6px;

    border-radius:50%;

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

    "Espacio":"#7e8c54",

    "Servicio":"#000000"


};

const nombresFicticios = {

    "Puerto Montt":"Fuerte Norte",
    "Puerto Varas":"Lago Claro",
    "Frutillar":"Bosque Azul",
    "Llanquihue":"Villa Horizonte",
    "Los Muermos":"Campo Norte",
    "Maullín":"Bahía Serena",
    "Calbuco":"Isla Bruma",
    "Cochamó":"Valle Neblina",
    "Fresia":"Valle Hermoso",
    "Puerto Octay":"Río Cristal",

    "Osorno":"Valle Central",
    "Purranque":"Río Dorado",
    "Puyehue":"Monte Claro",
    "Río Negro":"Bosque del Norte",
    "San Pablo":"Campo Azul",

    "Ancud":"Punta de lanza",
    "Castro":"Villa Estrella",
    "Chonchi":"Lago de estrellas",
    "Curaco de Vélez":"Isla Serena",
    "Dalcahue":"Puerto Niebla",
    "Puqueldón":"Isla Horizonte",
    "Queilén":"Bahía Clara",
    "Quellón":"Puerto Extremo",
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
            color: "#d9e6d5",
            weight: 1,
            fillColor: "#476b48",
            fillOpacity: 1
        },

	onEachFeature: function(feature, layer) {

            const comuna =
   		feature.properties["Comuna"] || "";

            const nombre =
                nombresFicticios[comuna] || comuna;

            if(nombre){

                layer.bindTooltip(
                    nombre,
                    {
                        permanent: true,
                        direction: "center",
                        className: "comuna-label",
			opacity:1
                    }
                );
	}

}

}).addTo(map);

    capaMapa.bringToBack();

    map.fitBounds(
        capaMapa.getBounds()
    );

})
.catch(error => {
    console.log(error);
});

nodos.forEach(n => {

    let color =
        colores[n.tipo] || "#888888";

    const marcador = L.circleMarker(
        [n.lat,n.lon],
        {
            radius:6,
            fillColor:color,
            color:"#ffffff",
            weight:2,
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

    marcador.bringToFront();

});
const legend = L.control({position:'bottomright'});

legend.onAdd = function () {

    const div = L.DomUtil.create('div','info legend');

    div.innerHTML = `

    <h4>Organizaciones</h4>

    <div><span style="background:#ff69b4"></span> Programa</div>

    <div><span style="background:#4CAF50"></span> Salud</div>

    <div><span style="background:#6ec6ff"></span> Judicial</div>

    <div><span style="background:#ffd54f"></span> Educación</div>

    <div><span style="background:#ff9800"></span> Comunitario</div>

    <div><span style="background:#ff8a80"></span> Seguridad</div>

    <div><span style="background:#7fffd4"></span> Gobierno local</div>

    <div><span style="background:#c7a17a"></span> Infancia</div>

    <div><span style="background:#c2185b"></span> Público</div>

    <div><span style="background:#556b2f"></span> Privada</div>

    <div><span style="background:#000000"></span> Servicio</div>

    `;

    return div;
};

legend.addTo(map);

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