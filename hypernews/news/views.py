import json
import random
import re
from collections import defaultdict
from datetime import datetime
from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse, Http404
from hypernews.settings import NEWS_JSON_PATH


class MainView(View):
    def get(self, request, *args, **kwargs):
        return redirect('/news/')


class NewsListView(View):
    def get(self, request, *args, **kwargs):
        with open(NEWS_JSON_PATH) as f:
            posts = json.load(f)

        q = request.GET.get('q')
        if q:
            print('q=', q)
            posts = [post for post in posts if re.search(q, post['title'], re.IGNORECASE)]

        posts_by_date = defaultdict(list)
        for post in posts:
            d = datetime.fromisoformat(post['created']).date().strftime("%Y-%m-%d")
            posts_by_date[d].append(post)

        for _, posts in posts_by_date.items():
            posts.sort(key=lambda x: x['created'], reverse=True)

        # posts_by_date.default_factory = None
        posts_by_date = sorted(posts_by_date.items(), reverse=True)
        print(posts_by_date)

        return render(request, "news/news_list.html", context={"dates": posts_by_date, 'test': "this is test"})


class NewsView(View):
    def get(self, request, *args, **kwargs):
        with open(NEWS_JSON_PATH) as f:
            posts = json.load(f)
        requested_post = None
        for post in posts:
            if post['link'] == kwargs['link']:
                requested_post = post
                break
        if requested_post is None:
            raise Http404

        return render(request, "news/detail.html", context=requested_post)


class AddNewsView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "news/create.html")

    def post(self, request, *args, **kwargs):
        with open(NEWS_JSON_PATH, 'r') as f:
            posts = json.load(f)
        title = request.POST.get('title')
        text = request.POST.get('text')

        if title and text:
            to_add = {
                'title': title,
                'text': text,
                'created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "link": random.randint(1, 100000),
            }
            posts.append(to_add)
            with open(NEWS_JSON_PATH, 'w') as f:
                json.dump(posts, f)
        return redirect("/news/")
