from django.http import JsonResponse
from django.db.models import Count
from .models import BlogPost

def tag_count_api(request):
    tag_counts = (
        BlogPost.objects.values('tags')
        .exclude(tags='')
        .annotate(count=Count('id', distinct=True))
        .order_by('-count')
    )
    # Split tags if comma separated, aggregate counts
    tag_agg = {}
    for entry in tag_counts:
        tags = [t.strip() for t in entry['tags'].split(',') if t.strip()]
        for tag in tags:
            tag_agg[tag] = tag_agg.get(tag, 0) + entry['count']
    tag_agg_list = [{'tag': tag, 'count': count} for tag, count in tag_agg.items()]
    tag_agg_list.sort(key=lambda x: -x['count'])
    return JsonResponse({'tags': tag_agg_list})

def author_count_api(request):
    author_counts = (
        BlogPost.objects.values('author__username')
        .annotate(count=Count('id', distinct=True))
        .order_by('-count')
    )
    return JsonResponse({'authors': list(author_counts)})
