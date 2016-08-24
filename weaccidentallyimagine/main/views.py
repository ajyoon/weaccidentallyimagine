import random

import blur
from django.http import HttpResponse, Http404
from django.template import loader
from django.utils import timezone

from .engine.soft_poem import SoftPoem
from .engine.poems import poems as poems_data


def main_view(request, seed=None):
    if not seed:
        # Assign a random seed that doesn't live in the URL
        # This seed will be passed to the permalinks in the template
        seed = random.randint(0, 1000000000000000000)
        is_fixed = False
    else:
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

    render_context = {
        'seed': seed,
        'is_fixed': is_fixed,
        'current_year': timezone.now().year,
        'poem_list': poems,
    }

    return HttpResponse(template.render(render_context, request))
