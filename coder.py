from shipping.models import *
from django.db.models import *
import json

def get_status(avt):
    print(avt)
    locs = list(
        avt.tree.run_set
        .filter(srctime__lt=avt.end,srctime__gt=avt.start)
        .values_list('locale', flat=True)
    )
    last_runs = dict(
        Locale.objects
        .filter(
            id__in=locs,
            run__tree=avt.tree,
            run__srctime__gt=avt.start,
            run__srctime__lt=avt.end,
        )
        .annotate(lr=Max('run'))
        .values_list('code', 'lr')
    )
    missing = dict(
        Run.objects
        .filter(id__in=last_runs.values())
        .annotate(m_total=F('missing') + F('missingInFiles'))
        .values_list('id', 'm_total')
    )
    return {
        'version': int(avt.appversion.version),
        'time': avt.end.isoformat(),
        'status': {
            loc: missing[run]
            for loc, run in last_runs.items()
        }
    }


print('hi')
b_old = Tree.objects.get(code='fx_beta_old')
beta = Tree.objects.get(code='fx_beta')

data = []
avts = b_old.appvers_over_time.filter(end__isnull=False).order_by('end')
for avt in avts:
    data.append(get_status(avt))
for avt in beta.appvers_over_time.filter(end__isnull=False).order_by('end'):
    data.append(get_status(avt))

with open('out.json', 'w') as fh:
    json.dump(data, fh, indent=0,sort_keys=True)
