from .models import UserProgress

def user_product(request):
    if request.user.is_authenticated:
        progress,_=UserProgress.objects.get_or_create(user=request.user)
        return {"product_user":{"authenticated":True,"name":request.user.get_short_name() or request.user.username,"level":progress.level,"xp":progress.xp,"coins":progress.coins}}
    return {"product_user":{"authenticated":False,"name":"Invitado","level":1,"xp":0,"coins":0}}
