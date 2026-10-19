from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .models import Post
from .forms import EmailPostForm, CommentForm, RegisterForm
from django.views.generic import ListView, TemplateView


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 2
    template_name = 'blog/post/list.html'



def post_detail(request, year, month, day, slug):
    post = get_object_or_404(Post, slug=slug,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)


    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == "POST":
        comment_form = CommentForm(
            data=request.POST,
            user=request.user,
        )

        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post

            # Use account details for signed-in users.
            # Guests can still enter their own name and email.
            if request.user.is_authenticated:
                new_comment.name = request.user.get_username()
                new_comment.email = request.user.email

            new_comment.save()
    else:
        comment_form = CommentForm(user=request.user)

    return render(
        request,
        "blog/post/detail.html",
        {
            "post": post,
            "comments": comments,
            "new_comment": new_comment,
            "comment_form": comment_form,
        },
    )


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            print(cd)
            post_url = request.build_absolute_uri(post.get_absolute_url())
            title = f"{cd['name']} sizga {post.title} ni o'qishni taklif etadi."
            message = f"{post.title} maqolasini o'qing: {post_url}\n\n" \
                      f"{cd['name']}ning izohi: {cd['comments']}"
            send_mail(title, message, 'azamatergashov1206@gmail.com', [cd['to']], fail_silently=False)
            sent = True

    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})

class HomeView(TemplateView):
    template_name = 'blog/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_posts'] = Post.published.all()[:3]
        return context


class AboutView(TemplateView):
    template_name = 'blog/about.html'



def _safe_auth_redirect(request):
    next_url = request.POST.get("next") or request.GET.get("next")

    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url

    return None


def register(request):
    if request.user.is_authenticated:
        return redirect("blogapp:post_list")

    next_url = request.POST.get("next") or request.GET.get("next", "")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            auth_login(request, user)

            return redirect(
                _safe_auth_redirect(request) or "blogapp:post_list"
            )
    else:
        form = RegisterForm()

    return render(
        request,
        "blog/auth/register.html",
        {
            "form": form,
            "next": next_url,
        },
    )


def user_login(request):
    if request.user.is_authenticated:
        return redirect("blogapp:post_list")

    next_url = request.POST.get("next") or request.GET.get("next", "")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            auth_login(request, form.get_user())

            return redirect(
                _safe_auth_redirect(request) or "blogapp:post_list"
            )
    else:
        form = AuthenticationForm(request)

    return render(
        request,
        "blog/auth/login.html",
        {
            "form": form,
            "next": next_url,
        },
    )


@require_POST
def user_logout(request):
    auth_logout(request)
    return redirect("home")

