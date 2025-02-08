from flask import Flask, request, jsonify
import pandas as pd
import requests
import openai
import os

app = Flask(__name__)

# Configurar la API de OpenAI desde una variable de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

# URL del archivo en Google Drive
URL_EXCEL = "https://drive.google.com/uc?export=download&id=12Cfiq2px1Lrdbjz5KXkJyr2FdeTkkiZY"

def descargar_excel(url):
    """ Descarga un archivo Excel desde una URL y lo carga en Pandas. """
    response = requests.get(url)
    with open("archivo.xlsx", "wb") as f:
        f.write(response.content)
    df = pd.read_excel("archivo.xlsx")
    return df

@app.route("/analizar", methods=["GET"])
def analizar():
    """ Descarga y analiza el archivo Excel """
    datos = descargar_excel(URL_EXCEL)
    resumen = datos.describe().to_string()
    return jsonify({"resumen": resumen})

@app.route("/preguntar", methods=["POST"])
def preguntar():
    """ Responde preguntas sobre el archivo Excel usando GPT """
    datos = descargar_excel(URL_EXCEL)
    pregunta = request.json.get("pregunta", "")
    contexto = f"Los datos del archivo Excel son:\n{datos.head(10).to_string()}\n\n"
    mensaje = contexto + "Responde la siguiente pregunta: " + pregunta

    respuesta = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un asistente experto en análisis de datos."},
            {"role": "user", "content": mensaje}
        ]
    )

    return jsonify({"respuesta": respuesta.choices[0].message.content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
