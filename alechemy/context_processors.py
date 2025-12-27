"""
Template context processors for Alechemy.
"""


def csp_nonce(request):
    """
    Add CSP nonce to template context.
    
    Usage in templates:
        <script nonce="{{ csp_nonce }}">
            // inline script
        </script>
        
        <style nonce="{{ csp_nonce }}">
            /* inline styles */
        </style>
    """
    return {
        'csp_nonce': getattr(request, 'csp_nonce', ''),
    }
