from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post
from .mixins import AuthorOnlyMixin

User = get_user_model()

NUMBER_OF_POSTS_PER_PAGE = 10


class IndexListView(ListView):
    paginate_by = NUMBER_OF_POSTS_PER_PAGE
    queryset = Post.published.all()
    template_name = 'blog/index.html'


class CategoryListView(ListView):
    paginate_by = NUMBER_OF_POSTS_PER_PAGE
    template_name = 'blog/category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

    def get_queryset(self):
        self.category = get_object_or_404(
            Category.published,
            slug=self.kwargs['category_slug'],
        )
        return Post.published.filter(category=self.category)


class PostDetailView(DetailView):
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context

    def get_object(self):
        post = get_object_or_404(
            Post.extended,
            pk=self.kwargs['post_id'],
        )
        if post.author == self.request.user:
            return post
        return get_object_or_404(
            Post.published,
            pk=self.kwargs['post_id'],
        )


class PostUpdateView(AuthorOnlyMixin, UpdateView):
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_object(self):
        return get_object_or_404(
            Post.extended,
            pk=self.kwargs['post_id'],
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.pk},
        )

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            self.kwargs['post_id'],
        )


class PostDeleteView(AuthorOnlyMixin, DeleteView):  # type: ignore
    template_name = 'blog/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = PostForm()
        form.instance = self.object
        context['form'] = form
        return context

    def get_object(self):
        return get_object_or_404(
            Post.extended,
            pk=self.kwargs['post_id'],
        )

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.object.author},
        )

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            self.kwargs['post_id'],
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(
            Post.extended,
            pk=self.kwargs['post_id'],
        )
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.pk},
        )


class CommentUpdateView(AuthorOnlyMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.pk},
        )

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            self.kwargs['post_id'],
        )


class CommentDeleteView(AuthorOnlyMixin, DeleteView):  # type: ignore
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.pk},
        )

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            self.kwargs['post_id'],
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.object.author},
        )


class ProfileListView(ListView):
    paginate_by = NUMBER_OF_POSTS_PER_PAGE
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username'],
        )
        if self.author == self.request.user:
            return Post.extended.filter(author=self.author)
        return Post.published.filter(author=self.author)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    fields = 'first_name', 'last_name', 'username', 'email'
    template_name = 'blog/user.html'

    def get_object(self):
        return get_object_or_404(
            User,
            pk=self.request.user.pk,
        )

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.object.username},
        )
