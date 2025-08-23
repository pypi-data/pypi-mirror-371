import json
import os
import subprocess
from pathlib import Path
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings


class ReactView(View):
    """
    Main view class for handling React SSR requests.
    Developers can override get_data method to fetch custom data.
    """
    
    def get_data(self, request):
        """
        Override this method to provide data to React components.
        Should return a dictionary that will be serialized to JSON.
        """
        return {
            'path': request.path,
            'method': request.method,
            'user': {
                'is_authenticated': request.user.is_authenticated,
                'username': request.user.username if request.user.is_authenticated else None,
            }
        }
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests with React SSR"""
        return self._render_react(request)
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests with React SSR"""
        return self._render_react(request)
    
    def _render_react(self, request):
        """Perform server-side rendering of React components"""
        try:
            # Get data for the React component
            data = self.get_data(request)
            
            # Path to the SSR script
            ssr_script_path = Path(__file__).parent / 'frontend' / 'ssr.js'
            
            if not ssr_script_path.exists():
                return HttpResponse(
                    "SSR script not found. Please run 'python manage.py reactbuild' first.",
                    status=500
                )
            
            # Prepare arguments for the SSR script
            url_path = request.path
            data_json = json.dumps(data)
            
            # Execute Node.js SSR script
            try:
                result = subprocess.run([
                    'node', 
                    str(ssr_script_path), 
                    url_path, 
                    data_json
                ], 
                capture_output=True, 
                text=True, 
                timeout=10
                )
                
                if result.returncode == 0:
                    rendered_html = result.stdout
                    
                    # Return the SSR content wrapped in the base template
                    return render(request, 'django_react_kit/index.html', {
                        'rendered_content': rendered_html,
                        'initial_data': data_json,
                        'path': url_path
                    })
                else:
                    error_message = result.stderr or "Unknown SSR error"
                    return HttpResponse(f"SSR Error: {error_message}", status=500)
                    
            except subprocess.TimeoutExpired:
                return HttpResponse("SSR timeout - the request took too long to process", status=500)
            except FileNotFoundError:
                return HttpResponse(
                    "Node.js not found. Please install Node.js to enable SSR functionality.", 
                    status=500
                )
                
        except Exception as e:
            return HttpResponse(f"Internal server error: {str(e)}", status=500)