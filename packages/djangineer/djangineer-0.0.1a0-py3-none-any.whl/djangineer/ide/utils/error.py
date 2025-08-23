from django.shortcuts import render

def render_error(request, message: str) -> dict:

    return render(
        request,
        'ide/partials/error.html',
        {'message': message}
    )