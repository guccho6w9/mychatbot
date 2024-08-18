from django.shortcuts import render, reverse
import requests
from .models import ChatBot
from django.http import HttpResponseRedirect, JsonResponse
import logging
import google.generativeai as genai
import os


logger = logging.getLogger(__name__)
# Configurar Gemini usando la variable de entorno
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
def ask_question(request):
    if request.method == "POST":
        text = request.POST.get("text")
        logger.info(f"User input: {text}")

        # Extraer el tema/genre si está en la consulta
        if "libros de" in text.lower():
            genre = text.lower().split("libros de")[-1].strip()
        else:
            genre = text.strip()

        logger.info(f"Extracted genre: {genre}")


        api_key= os.getenv('GOOGLE_API_KEY')
        url = f'https://www.googleapis.com/books/v1/volumes?q={genre}&key={api_key}'
        response = requests.get(url)
        data = response.json()
        books = data.get('items', [])

        logger.info(f"Google Books API response: {data}")

        recommendations = [{'title': book['volumeInfo']['title'],
                            'authors': book['volumeInfo'].get('authors', []),
                            'description': book['volumeInfo'].get('description', 'No description available')}
                           for book in books[:5]]  # Limitar a 5 recomendaciones

        # Combinar recomendaciones de libros con la respuesta de Gemini
        model = genai.GenerativeModel("gemini-pro")
        chat = model.start_chat()
        gemini_response = chat.send_message(text)
        logger.info(f"Gemini Response: {gemini_response.text}")

        # Guardar la consulta y la respuesta en la base de datos
        ChatBot.objects.create(text_input=text, gemini_output=gemini_response.text)

        response_data = {
            "text": gemini_response.text,
            "recommendations": recommendations
        }

        return JsonResponse({"data": response_data})
    else:
        return HttpResponseRedirect(reverse("chat"))

def chat_view(request):
    return render(request, 'chat/chat.html')  # Renderizar la plantilla HTML básica

def chat(request):
    chats = ChatBot.objects.all()  # Remove user filter
    return render(request, "chat_bot.html", {"chats": chats})

def recommend_books(request):
    if request.method == 'POST':
        query = request.POST.get('query')

        # Filtrar la consulta para extraer el tema/genre.
        if "libros de" in query:
            genre = query.split("libros de")[-1].strip()  # Extrae el tema después de "libros de"
        else:
            genre = query.strip()  # Usa la consulta completa si no se detecta el patrón

        api_key = os.getenv('GOOGLE_API_KEY')
        url = f'https://www.googleapis.com/books/v1/volumes?q={genre}&key={api_key}'
        response = requests.get(url)
        data = response.json()
        books = data.get('items', [])

        logger.info(f"Google Books API response for recommend_books: {data}")

        recommendations = [{'title': book['volumeInfo']['title'],
                            'authors': book['volumeInfo'].get('authors', []),
                            'description': book['volumeInfo'].get('description', 'No description available')}
                           for book in books[:5]]  # Limitar a 5 recomendaciones

        return JsonResponse({'books': recommendations})
    return JsonResponse({'error': 'Invalid request'}, status=400)
