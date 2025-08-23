from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import os
from .utils.error import render_error

def home_view(request):
    print(os.environ.get("DJANGINEER_PROJECT_PATH"))
    env_project_path = os.environ.get("DJANGINEER_PROJECT_PATH", "")
    request.session["project_path"] = env_project_path
    return render(request, 'ide/home.html')

# def open_project(request):
#     """
#     Opens the project in the IDE.
#     """
#     project_path = request.session.get("project_path", "")
#     if not project_path:
#         render_error(request, "Project path is not set")
