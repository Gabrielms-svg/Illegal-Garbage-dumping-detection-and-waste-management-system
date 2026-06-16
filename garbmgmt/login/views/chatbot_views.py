from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..chatbot import get_response


@csrf_exempt
def chatbot_api(request):
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'Invalid request'}, status=400)

        user_message = request.POST.get('message', '')
        reply = get_response(user_message)
        return JsonResponse({'reply': reply})

    except Exception as e:
        return JsonResponse({'error': 'An internal error occurred. Our assistant is temporarily unavailable.'}, status=500)
