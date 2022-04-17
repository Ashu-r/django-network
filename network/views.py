import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, Post, Comment
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict


def index(request):
    page = request.GET.get('page', 1)
    paginator = Paginator(Post.objects.all(), 10)
    posts = paginator.page(page).object_list
    pageRange = paginator.page_range
    hasPrevious = paginator.page(page).has_previous()
    hasNext = paginator.page(page).has_next()
    postsNew = []
    for p in posts:
        postsNew.append({**model_to_dict(p), "likes": p.likes.all(),
                        "isLiked": p.likes.filter(username=request.user.username).exists()})
    if request.user.is_authenticated:
        currentUser = {**model_to_dict(request.user)}
    else:
        currentUser = None
    print(postsNew)
    return render(request, "network/index.html", {'posts': postsNew, 'page': int(page), 'hasPrevious': hasPrevious, 'hasNext': hasNext, 'pageRange': pageRange, 'currentUser': currentUser})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


@login_required
def new_post(request):
    if request.method == "POST":
        user = request.user
        title = request.POST["title"]
        content = request.POST["content"]

        post = Post(user=user, title=title, content=content)
        post.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/new_post.html")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def user(request, username):
    user = User.objects.get(username=username)
    isFollowing = False
    if request.user.following.filter(username=username).exists():
        isFollowing = True
    return render(request, "network/user.html", {
        "username": username,
        "posts": Post.objects.filter(user=user),
        "following": user.following.all(),
        "followers": user.followers.all(),
        "isFollowing": isFollowing
    })


@login_required
def follow(request, username):
    user = User.objects.get(username=username)
    print(request.method)
    if request.method == "POST":
        if request.user.following.filter(username=username).exists():
            request.user.following.remove(user)
        else:
            request.user.following.add(user)
        print(request.user.following.all())
        return HttpResponseRedirect(reverse("user", args=(username,)))
    else:
        return HttpResponseRedirect(reverse("user", args=(username,)))


@login_required
def following(request):
    posts = Post.objects.filter(user__in=request.user.following.all())
    return render(request, "network/index.html", {'posts': posts})


@csrf_exempt
@login_required
def edit(request, id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    post = Post.objects.get(id=id)
    if post.user != request.user:
        return JsonResponse({"error": "You do not have permission to edit this post."}, status=403)

    post.content = data["content"]
    post.save()
    return JsonResponse({"success": "Post updated successfully.",
                         "content": post.content,
                         }, status=200)


@csrf_exempt
@login_required
def like(request, id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    post = Post.objects.get(id=id)
    if post.likes.filter(username=request.user.username).exists():
        post.likes.remove(request.user)
        post.save()
        return JsonResponse({"success": "Post unliked successfully.", "action": "like", "likes": post.likes.count()}, status=200)
    else:
        post.likes.add(request.user)
        post.save()
        return JsonResponse({"success": "Post liked successfully.",
                             "action": "unlike",
                             "likes": post.likes.count(),
                             }, status=200)
