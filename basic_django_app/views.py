

from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from .models import BlogPost, LikeDislike, Comment, CommentLikeDislike
from django.views.decorators.http import require_POST

def index(request):
    if request.user.is_authenticated:
        # Handle new blog post creation
        if request.method == 'POST' and request.POST.get('action') == 'create_post':
            title = request.POST.get('title')
            body = request.POST.get('body')
            tags = request.POST.get('tags')
            if title and body:
                BlogPost.objects.create(title=title, body=body, tags=tags or '', author=request.user)
                return redirect('/')
        # Handle blog post deletion
        if request.method == 'POST' and request.POST.get('action', '') == 'delete_post':
            post_id = request.POST.get('post_id')
            try:
                post = BlogPost.objects.get(id=post_id, author=request.user)
                post.delete()
            except BlogPost.DoesNotExist:
                pass
            return redirect('/')
        # Handle like/dislike for posts
        if request.method == 'POST' and request.POST.get('action') in ['like', 'dislike'] and request.POST.get('post_id'):
            post_id = request.POST.get('post_id')
            value = 1 if request.POST.get('action') == 'like' else -1
            post = BlogPost.objects.get(id=post_id)
            obj, created = LikeDislike.objects.update_or_create(user=request.user, post=post, defaults={'value': value})
            return redirect('/')
        # Handle like/dislike for comments
        if request.method == 'POST' and request.POST.get('action') in ['like_comment', 'dislike_comment'] and request.POST.get('comment_id'):
            comment_id = request.POST.get('comment_id')
            value = 1 if request.POST.get('action') == 'like_comment' else -1
            comment = Comment.objects.get(id=comment_id)
            obj, created = CommentLikeDislike.objects.update_or_create(user=request.user, comment=comment, defaults={'value': value})
            # Redirect to the same post and open comments section
            return redirect(f'/?open_comments={comment.post.id}')
        # Handle comment
        if request.method == 'POST' and request.POST.get('action') == 'comment':
            post_id = request.POST.get('post_id')
            comment_text = request.POST.get('comment_text')
            if comment_text:
                post = BlogPost.objects.get(id=post_id)
                Comment.objects.create(post=post, user=request.user, text=comment_text)
            return redirect('/')
        sort = request.GET.get('sort', 'newest')
        tag_filter = request.GET.get('tag', '').strip()
        posts_qs = BlogPost.objects.all()
        if tag_filter:
            posts_qs = posts_qs.filter(tags__icontains=tag_filter)
        if sort == 'most_liked':
            posts_qs = sorted(posts_qs, key=lambda p: p.likes_dislikes.filter(value=1).count(), reverse=True)
        elif sort == 'most_disliked':
            posts_qs = sorted(posts_qs, key=lambda p: p.likes_dislikes.filter(value=-1).count(), reverse=True)
        else:
            posts_qs = posts_qs.order_by('-created_at')
        open_comments = request.GET.get('open_comments')
        post_data = []
        for post in posts_qs:
            likes = post.likes_dislikes.filter(value=1).count()
            dislikes = post.likes_dislikes.filter(value=-1).count()
            comments = []
            for comment in post.comments.order_by('-created_at'):
                c_likes = comment.likes_dislikes.filter(value=1).count()
                c_dislikes = comment.likes_dislikes.filter(value=-1).count()
                c_user_like = None
                if request.user.is_authenticated:
                    try:
                        c_user_like = CommentLikeDislike.objects.get(user=request.user, comment=comment).value
                    except CommentLikeDislike.DoesNotExist:
                        c_user_like = None
                comments.append({
                    'comment': comment,
                    'likes': c_likes,
                    'dislikes': c_dislikes,
                    'user_like': c_user_like,
                })
            user_like = None
            if request.user.is_authenticated:
                try:
                    user_like = LikeDislike.objects.get(user=request.user, post=post).value
                except LikeDislike.DoesNotExist:
                    user_like = None
            post_data.append({
                'post': post,
                'likes': likes,
                'dislikes': dislikes,
                'comments': comments,
                'user_like': user_like,
                'open_comments': str(post.id) == open_comments,
            })
        return render(request, 'basic_django_app/home.html', {
            'user': request.user,
            'message': request.GET.get('message'),
            'posts': post_data,
            'sort': sort,
            'tag_filter': tag_filter,
        })
    error = None
    message = request.GET.get('message')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error = 'Invalid username or password.'
    return render(request, 'basic_django_app/login.html', {'error': error, 'message': message})

def logout_view(request):
    logout(request)
    return redirect('/?message=Thank you for using Basic Django App!')


def create_account(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            error = 'Username and password are required.'
        elif User.objects.filter(username=username).exists():
            error = 'Username already in use. Please pick a new one.'
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('/')
    return render(request, 'basic_django_app/create_account.html', {'error': error})
