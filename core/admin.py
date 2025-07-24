from django.contrib import admin
from .models import User, Post, Comment, Vote

# Define a custom admin class for the Post model
class PostAdmin(admin.ModelAdmin):
    # Fields to display in the main list view of all posts
    list_display = ('title', 'author', 'post_type', 'created_at')
    
    # Fields to make searchable in the admin
    search_fields = ('title', 'content')
    
    # Fields that can be used to filter the list of posts
    list_filter = ('post_type', 'created_at')
    
    # This explicitly defines the fields and their order on the "Add/Edit Post" page
    # Crucially, it tells Django to render the 'author' field as a dropdown
    fields = ('author', 'title', 'content', 'post_type')

# Register your models with the admin site
admin.site.register(User)
admin.site.register(Post, PostAdmin) 
admin.site.register(Comment)
admin.site.register(Vote)