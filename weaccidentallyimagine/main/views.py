"""Views for the application. (Just one view!)"""

import random

import blur
from django.http import HttpResponse, Http404
from django.template import loader
from django.utils import timezone

from .engine.soft_poem import SoftPoem
from .engine.poems import poems as poems_data


def main_view(request, seed=None):
    """The main (and only) view of the application.

    Renders a version of the book either from a random new seed or from
    a fixed seed if passed by the URL router.

    Args:
        request (django.http.HttpRequest): Request object passed automatically
            by URL routing magic.
        seed (Optional[str of digits]): If present, the numerical seed which
            is passed to the global random state to allow fully reproducible
            rendering of a specific version of the book.

    Returns:
        django.http.HttpResponse
    """
    if not seed:
        # Assign a random seed that doesn't live in the URL
        # This seed will be passed to the permalinks in the template
        seed = random.randint(0, 1000000000000000000)
        is_fixed = False
    else:
        # Be sure to cast str to int
        seed = int(seed)
        is_fixed = True
    # Now apply the seed
    random.seed(seed)
    # Load the template
    template = loader.get_template('main/poem_page.html')
    # Load a list of all of the poems
    poems = [SoftPoem(**kwargs) for kwargs in poems_data]
    # Order poems
    poems = blur.rand.weighted_order([(poem, poem.position_weight)
                                      for poem in poems])
    # Set up context variables to pass to template rendering
    render_context = {
        'seed': seed,
        'is_fixed': is_fixed,
        'current_year': timezone.now().year,
        'poem_list': poems,
    }
    return HttpResponse(template.render(render_context, request))
