from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from .models import Post, Category, User, Comment
from django.utils import timezone
from django.core.paginator import Paginator
from .forms import PostForm, CommentForm, UserForm
from django.contrib.auth.decorators import login_required


NUMBER_OF_PAGINATOR_PAGES = 10


def index(request):
    template = 'blog/index.html'

    posts = Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).annotate(comment_count=Count('comments')
               ).order_by('-pub_date')

    categories = {}
    if posts:
        category_ids = posts.values_list('category_id', flat=True)
        categories = {cat.id: cat for cat in Category.objects.filter(
            id__in=category_ids)}
    page_obj = get_paginator(request, posts)
    context = {
        'page_obj': page_obj,
        'categories': categories,
    }

    return render(request, template, context)


def post_detail(request, id):
    template = 'blog/detail.html'
    post = get_object_or_404(Post, pk=id)
    if request.user != post.author:
        post = get_object_or_404(
            Post,
            id=id,
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now())
    form = CommentForm(request.POST or None)
    comments = Comment.objects.select_related(
        'author').filter(post=post)
    context = {'post': post,
               'form': form,
               'comments': comments}
    return render(request, template, context)


def profile(request, username):
    template = 'blog/profile.html'
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(
        author=user
    ).annotate(comment_count=Count('comments')
               ).order_by('-pub_date')
    if request.user != user:
        posts = Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
            author=user).annotate(comment_count=Count('comments')
                                  ).order_by('-pub_date')
    page_obj = get_paginator(request, posts)
    context = {'user': user,
               'page_obj': page_obj}
    return render(request, template, context)


@login_required
def edit_profile(request):
    profile = get_object_or_404(
        User,
        username=request.user)
    form = UserForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', request.user)
    context = {'form': form}
    return render(request, 'blog/user.html', context)


@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', request.user)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    posts = Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
        category__slug__exact=category_slug

    ).order_by('-pub_date')

    categories = get_object_or_404(Category,
                                   is_published=True,
                                   slug__exact=category_slug
                                   )
    page_obj = get_paginator(request, posts)
    context = {
        'page_obj': page_obj,
        'categories': categories,
    }

    return render(request, template, context)


def get_paginator(request, queryset,
                  number_of_pages=NUMBER_OF_PAGINATOR_PAGES):
    paginator = Paginator(queryset, number_of_pages)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@login_required
def edit_post(request, id):
    post = get_object_or_404(Post, id=id)
    if request.user != post.author:
        return redirect('blog:post_detail', id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, id):
    post = get_object_or_404(Post, id=id)
    if request.user != post.author:
        return redirect('blog:post_detail', id)
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, id):
    post = get_object_or_404(Post, id=id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', id)


@login_required
def edit_comment(request, id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id)
    context = {'comment': comment,
               'form': form}
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id)
    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)
