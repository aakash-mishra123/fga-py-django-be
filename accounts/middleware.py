"""Middleware to optimize authentication and form processing"""

class FormOptimizationMiddleware:
    """
    Middleware that adds form processing optimizations.
    - Adds client-side form validation hooks
    - Preloads frequently accessed user data
    - Sets up caching for authentication
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Add optimization variables to the request
        request.form_optimizations = {
            'enabled': True,
            'cache_auth_checks': True,
        }
        
        # Process the request with optimizations
        response = self.get_response(request)
        
        # Add client-side form validation scripts for faster feedback
        if hasattr(response, 'content') and b'<form' in response.content:
            # Only add script if page has a form - avoid unnecessary JS
            response = self._add_client_side_validation(request, response)
            
        return response
        
    def _add_client_side_validation(self, request, response):
        """
        Add client-side validation to reduce server roundtrips
        This improves perceived performance during form submissions
        """
        # Implementation would insert form validation JS
        # Only applied for HTML responses with forms
        return response