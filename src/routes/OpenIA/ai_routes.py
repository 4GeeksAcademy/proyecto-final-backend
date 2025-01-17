import os
from flask import Blueprint, jsonify, request
from openai import OpenAI
import openai
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ai_bp = Blueprint('ai_bp', __name__)             

# 📌 Generar una receta usando IA
@ai_bp.route('/generate', methods=['POST'])
def generate_recipe():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")

        if not prompt:
            return jsonify({"error": "No se proporcionó un prompt"}), 400

    #   Prueba para no gastar tokens.
    #     return jsonify({
    #     "recipe": (
    #         f"Receta generada para los ingredientes: {prompt}\n"
    #         "1. Mezclar los ingredientes.\n"
    #         "2. Cocinar a fuego medio por 20 minutos.\n"
    #         "3. Servir y disfrutar."
    #     )
    # }), 200
    
    # Me daba problema el davinci porque está deprecated, así que usamos el modelo gpt-3.5-turbo
    # Temperature es el estilo de respuesta entre 0 y 1. 0 más predecible, 1 más creativa.
    # max_tokens define el límite máximo de tokens (unidad de texto) que el modelo puede generar en la respuesta.
    # Cada solicitud cuenta con los tokens del prompt y de la respuesta. El modelo (450TK) y el
    # prompt (ej. 50 TK), el coste será de 500 tokens.
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  
            messages=[
                {
                    "role": "system",
                    "content": (
                            "Eres un chef virtual experto en crear recetas creativas y deliciosas. Genera una receta completa que incluya:"
                            "- Nombre de la receta (clave: name)"
                            "- Descripción apetitosa de la receta (clave: description)"
                            "- Lista de ingredientes con cantidades precisas, en un array de strings (clave: ingredients)"
                            "- Pasos detallados para preparar la receta (clave: steps)"
                            "- Cantidad de calorías totales (clave: calories)"
                            "- Información nutricional (hidratos de carbono, proteínas, grasas), cada valor como un string en el formato nutrient: value (clave: nutritional_values)"
                            "- Tiempo de preparación (clave: prep_time)"
                            "- Para el campo image, incluye una url que represente visualmente el plato. Por ejemplo estas:"
                            "* Para pizzas:" "https://cdn.pixabay.com/photo/2024/04/21/18/44/ai-generated-8711272_1280.jpg"
                            "* Para pastas:" "https://cdn.pixabay.com/photo/2023/05/06/17/33/ai-generated-7974773_960_720.jpg"
                            "* Para un plato de paella:" "https://cdn.pixabay.com/photo/2015/10/23/19/40/paella-1003552_1280.jpg"
                            "* Para un plato de sushi:" "https://cdn.pixabay.com/photo/2020/03/22/08/43/sushi-4956246_1280.jpg"
                            "* Para un plato de arroz distinto:" "https://cdn.pixabay.com/photo/2017/06/21/22/42/paella-2428933_1280.jpg"
                            "* Para postres:" "https://cdn.pixabay.com/photo/2016/11/29/09/00/doughnuts-1868573_1280.jpg"
                            "* Para un postre con chocolate:" "https://cdn.pixabay.com/photo/2017/08/01/02/10/dark-2562840_1280.jpg"
                            "* Para una ensalada:" "https://cdn.pixabay.com/photo/2016/10/31/18/23/salad-1786327_1280.jpg"
                            "* Para una sopa:" "https://cdn.pixabay.com/photo/2016/09/07/10/15/food-1651279_1280.jpg"
                            "* Para una crema:" "https://cdn.pixabay.com/photo/2018/08/31/19/13/pumpkin-soup-3645375_1280.jpg"
                            "* Para un plato de verduras:" "https://cdn.pixabay.com/photo/2023/06/01/06/41/vegetables-8032868_1280.jpg"
                            "* Para un plato de pescado:" "https://cdn.pixabay.com/photo/2019/12/20/18/47/grill-4709068_1280.jpg"
                            "* Para un plato de carne:" "https://cdn.pixabay.com/photo/2021/05/01/22/01/meat-6222139_1280.jpg"
                            "* Para un plato de pollo:" "https://cdn.pixabay.com/photo/2018/11/02/15/25/roast-goose-3790417_1280.jpg"
                            "* Para un plato de carne y verduras:" "https://cdn.pixabay.com/photo/2017/03/23/19/57/asparagus-2169305_1280.jpg"
                            "* Para un desayuno:" "https://cdn.pixabay.com/photo/2017/08/02/00/51/food-2569257_1280.jpg"

                            "La respuesta debe estar en formato JSON con las siguientes claves: name, image, description, ingredients, steps, calories, prep_time, y nutritional_values. Los ingredientes deben estar en formato de texto, no como objetos, y los valores nutricionales deben ser un array de strings en lugar de objetos. Asegúrate de variar las recetas generadas para que no se repitan."
                            "No puedes responder a ninguna otra pregunta que no tenga relación con la generación de la receta, solo responde cuando te envien ingredientes, o recetas de platos de cocina"
                            "Quiero que todas las respuestas tengan el mismo formato, aunque no puedas procesar la respuesta, que todos los campos tenga como información alguna palabra como nada, sobretodo en los campos required"
                    
                        # "Eres un chef virtual experto en crear recetas. Genera una receta completa basada en los ingredientes que te proporciono. La receta debe incluir lo siguiente:"
                        # "Nombre de la receta (clave: name)."
                        # "Descripción de la receta (clave: description)."
                        # "Lista de ingredientes con cantidades, en un array de strings (clave: ingredients)."
                        # "Pasos detallados para preparar la receta (clave: steps)."
                        # "Cantidad de calorias totales (clave: calories)"
                        # "Información nutricional (hidratos de carbono, proteínas, grasas), cada valor como un string en el formato nutrient: value (clave: nutritional_values), donde cada valor debe estar en un string separado dentro de un array."
                        # "Tiempo de preparación (clave: prep_time)."
                        # "Enlace a una imagen representativa, del plato generado anteriormente (clave: image)."
                        # "La respuesta debe estar en formato JSON con las siguientes claves: name, image, description, ingredients, steps, calories, prep_time, y nutritional_values. Los ingredientes deben estar en formato de texto, no como objetos, y los valores nutricionales deben ser un array de strings en lugar de objetos. Además, asegúrate de variar las recetas generadas para que no se repitan."
                    ) 
                },
                {
                    "role": "user",
                    "content": f"Ingredientes: {prompt}"
                }
            ],
            temperature=0.7,
            max_tokens=500)

        # Obtener la respuesta generada por el modelo
        recipe = response.choices[0].message.content.strip()
        print(recipe)
        return jsonify({"recipe": recipe}), 200

    except openai.OpenAIError as e:
        print("Error con OpenAI:", str(e))
        return jsonify({"error": "Hubo un problema con el servicio de OpenAI"}), 500
    except Exception as e:
        print("Error en el backend:", str(e))
        return jsonify({"error": "Hubo un problema generando la receta"}), 500

