"""serve the network app views"""
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post
from .forms import UserForm, PostForm


def index(request, pnum=1):
    """main page of posts"""
    # blank PostForm
    postform = PostForm()
    post_list = Post.objects.annotate(Count('likes')).order_by('-timestamp')
    pdata = pagehelper(post_list, pnum, 'index') # helper function below
    return render(request, "network/index.html", {
        "postform": postform,
        "pdata": pdata
    })

def login_view(request):
    """log in"""
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
    """logout"""
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """register a new User"""
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

@csrf_exempt
def profile(request, name, pnum=1):
    """display a specific user's profile"""
    if request.method == "GET":
        user_obj = User.objects.get(username=name)
        # all posts by target user passed in param
        post_list = Post.objects.annotate(
                    Count('likes')).filter(
                    user=user_obj).order_by('-timestamp')
        # package data needed to display posts - reroute to profile route
        pdata = pagehelper(post_list, pnum, 'profile')
        return render(request, "network/profile.html", {
            "user_obj": user_obj,
            "pdata": pdata
        })

@login_required
def editprofile(request):
    """update a user's profile info"""
    user = request.user

    if request.method == "POST":
        # get the form from request; the image file from POST; the User is THIS user
        form = UserForm(request.POST, request.FILES or None, instance=user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))

        # invalid form - return form to user (django automatically rejects repeat usernames)
        return render(request, "network/editprofile.html", {
        "userform": form
        })

    # request method GET: display this user's profile info
    userform = UserForm(instance=user)
    return render(request, "network/editprofile.html", {
        "userform": userform
    })

@login_required
def post(request):
    """submit a new Post"""
    # should only be a post request
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            # if form info is valid: save the instance, add the user, save
            newpost = form.save(commit=False)
            newpost.user = request.user
            newpost.save()
            return HttpResponseRedirect(reverse("index"))

@login_required
def following(request, pnum=1):
    """display posts by all users THIS user follows"""
    user = request.user
    userlist = user.following.all() # all users this user follows
    # all posts by followed users, reverse chronological order
    post_list = Post.objects.annotate(
                Count('likes')).filter(
                user__in=userlist).order_by('-timestamp')
    # first page by default. Redirect to 'following' in paginate.html
    pdata = pagehelper(post_list, pnum, 'following')
    return render(request, "network/following.html", {
        "pdata": pdata
    })

@csrf_exempt
def follow(request, name):
    """Add follower, remove follower, or update follow count"""
    # target user passed from parameter, this user from request
    targetuser = User.objects.get(username=name)
    thisuser = request.user

    # if adding or removing follower:
    if request.method == "PUT":
        # update whether viewing user follows/unfollows target user
        data = json.loads(request.body)
        if data.get("addfollow") is not None:
            # request user should follow target user
            thisuser.following.add(targetuser)
            thisuser.save()
            return JsonResponse({"message": "Follower added successfully"}, status=201)
        if data.get("unfollow") is not None:
            # request user should UNfollow target user
            thisuser.following.remove(targetuser)
            return JsonResponse({"message": "Unfollowed successfully"}, status=201)
    elif request.method == "GET":
        # users following, and followed by, target user
        followingnum = targetuser.following.all().count()
        followersnum = targetuser.followers.all().count()
        followbool = thisuser in targetuser.followers.all()
        # pass these values into JSON response
        return JsonResponse({
            "followingnum": followingnum,
            "followersnum": followersnum,
            "followbool": followbool
            }, status=201)

@csrf_exempt
@login_required
def like(request, pk):
    """ Like or unlike a post, update like count and like status"""
    xpost = Post.objects.get(pk=pk)
    user = request.user
    # if request method PUT: this user likes/unlikes this post
    if request.method == "PUT":
        if user not in xpost.likes.all():
            xpost.likes.add(user)
        else:
            xpost.likes.remove(user)
        likenum = xpost.likes.all().count()
        return JsonResponse({
            "likenum": likenum
        }, status=201)

@csrf_exempt
@login_required
def update(request, pk):
    """API route to update a user's previous post"""
    # updating a post must be through PUT request
    if request.method != "PUT":
        return JsonResponse({"error": "PUT fetch required."}, status=400)
    xpost = Post.objects.get(pk=pk)
    # if Post poster and request user don't match, reject
    if request.user != xpost.user:
        return JsonResponse({"error": "Can't edit another user's post"}, status=400)
    data = json.loads(request.body)
    if data.get('newtext') is not None:
        xpost.body = data.get('newtext')
        xpost.save(update_fields=['body'])
    return JsonResponse({"message": " success"}, status=201)


def pagehelper(post_list, pnum, route):
    """return a dictionary for displaying 10 posts at a time,
    given any queryset, page number, and which route for posts"""
    # https://docs.djangoproject.com/en/3.0/topics/pagination/
    paginator = Paginator(post_list, 10)
    page_list = paginator.get_page(pnum) # this particular list of 10 posts
    prev_page = pnum - 1 # page number (int) of previous page
    next_page = pnum + 1 # page number (int) of next page
    has_next = page_list.has_next() # boolean: is there another list of 10 after this?
    return {"pnum": pnum, "route": route, "page_list": page_list, "prev_page": prev_page,
            "next_page": next_page, "has_next": has_next}
