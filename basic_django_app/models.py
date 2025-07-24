from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def get_display_name(self):
        if self.display_name:
            return self.display_name
        elif self.user.first_name:
            return self.user.first_name
        else:
            return self.user.username

class UserSentimentPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sentiment_preference')
    positive_views = models.PositiveIntegerField(default=0)
    negative_views = models.PositiveIntegerField(default=0)
    neutral_views = models.PositiveIntegerField(default=0)

    def get_preferred_sentiment(self):
        counts = {
            'positive': self.positive_views,
            'negative': self.negative_views,
            'neutral': self.neutral_views,
        }
        # Return the sentiment with the highest count, default to 'neutral' if tie
        return max(counts, key=lambda k: (counts[k], k))

class LikedAuthor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_authors')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_by_users')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'author')

class LikedTag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_tags')
    tag = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tag')

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    tags = models.CharField(max_length=200, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    sentiment = models.CharField(max_length=16, default='neutral')

    def __str__(self):
        return self.title

    def update_sentiment(self):
        from .sentiment import analyze_sentiment
        self.sentiment = analyze_sentiment(f"{self.title}\n{self.body}")
        self.save(update_fields=["sentiment"])

class LikeDislike(models.Model):
    LIKE = 1
    DISLIKE = -1
    VALUE_CHOICES = ((LIKE, 'Like'), (DISLIKE, 'Dislike'))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='likes_dislikes')
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

class CommentLikeDislike(models.Model):
    LIKE = 1
    DISLIKE = -1
    VALUE_CHOICES = ((LIKE, 'Like'), (DISLIKE, 'Dislike'))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes_dislikes')
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')
