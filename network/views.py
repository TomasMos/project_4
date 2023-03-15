from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from .models import User, Post, Follow, Like
import json
from django.http import JsonResponse


def index(request):
    all_posts = Post.objects.all().order_by("id").reverse()

    # use pagination
    p = Paginator(all_posts, 10)
    page_num = request.GET.get('page', 1)
    page = p.page(page_num)

    likes = Like.objects.all()

    liked = []
    try:
        for like in likes:
            if like.user.id == request.user.id:
                liked.append(like.post.id)
    except:
        liked = []

    return render(request, "network/index.html", {
        "all_posts": page,
        "liked": liked,
    })


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


def new_post(request):
    if request.method == "POST":
        body = request.POST["body"]
        user = User.objects.get(pk=request.user.id)
        post = Post(author = user, body = body)
        post.save()

        return HttpResponseRedirect(reverse(index))
    else:
        return HttpResponseRedirect(reverse(index))

def profile(request, user_id):

    request_user = User.objects.get(pk=request.user.id)
    user = User.objects.get(pk=user_id)
    # user_followed = user.username

    if request.method == 'POST':
        try:
            if request.POST['follow'] == 'F':
                f = Follow(user_followed=user, user_following = request_user)
                f.save()
            else:
                f = Follow.objects.get(user_followed=user, user_following = request_user)
                f.delete()
        except:
            return HttpResponseRedirect(reverse(profile, kwargs = {"user_id": user.id}))



    all_posts = Post.objects.filter(author = user).order_by("id").reverse()
    following = Follow.objects.filter(user_following = user)
    followers = Follow.objects.filter(user_followed = user)

    try:
        num = followers.filter(user_following=request.user)
        if len(num) != 0:
            sheep = True
        else:
            sheep = False
    except:
        sheep = False

    return render(request, "network/profile.html", {
        "user": user,
        "all_posts": all_posts,
        "following": following,
        "followers": followers,
        "sheep": sheep
    })

def following(request):
    user = User.objects.get(pk=request.user.id)
    follows = Follow.objects.filter(user_following = user)
    all_posts = Post.objects.all().order_by("id").reverse()

    followed_posts = []
    for person in follows:
        print(person)
        for post in all_posts:
            print(f"{post.author} made {post}")
            if post.author == person.user_followed:
                followed_posts.append(post)

    # use pagination
    p = Paginator(followed_posts, 10)
    page_num = request.GET.get('page', 1)
    page = p.page(page_num)

    return render(request, "network/following.html", {
        "all_posts": page
    })

def edit(request, post_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        edit = Post.objects.get(pk=post_id)
        print(data)
        edit.body = data["content"]
        edit.save()
        return JsonResponse({"message": "Change Successful", "data": data["content"]})


def like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk = request.user.id)
    newlike = Like(user = user, post = post)
    newlike.save()
    print("uyes")
    return JsonResponse({"message": "Successfully liked"})




def unlike(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk = request.user.id)
    oldlike = Like.objects.filter(user = user, post = post)
    oldlike.delete()
    return JsonResponse({"message": "Successfully unliked"})