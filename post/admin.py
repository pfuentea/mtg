from django.contrib import admin
from post.models import Post
# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display=('id','title')

    #list_filter =("status")
    #search_fields= ['title','content']
    #prepopulated_fields ={'slug':('title',)}