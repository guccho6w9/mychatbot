from django.shortcuts import render, reverse
import requests
from .models import ChatBot
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import google.generativeai as genai


genai.configure(api_key="AIzaSyBASv6CqYAbsxdkNTiidFn9UuA9luoXPnk")


def ask_question(request):
    if request.method == "POST":
        text = request.POST.get("text")
        model = genai.GenerativeModel("gemini-pro")
        chat = model.start_chat()
        response = chat.send_message(text)
        ChatBot.objects.create(text_input=text, gemini_output=response.text)
        response_data = {
            "text": response.text,  # Assuming response.text contains the relevant response data
        }
        return JsonResponse({"data": response_data})
    else:
        return HttpResponseRedirect(reverse("chat"))  # Redirect to chat page for GET requests


def chat_view(request):
    return render(request, 'chat/chat.html')  # Renderizar la plantilla HTML básica

def chat(request):
    chats = ChatBot.objects.all()  # Remove user filter
    return render(request, "chat_bot.html", {"chats": chats})