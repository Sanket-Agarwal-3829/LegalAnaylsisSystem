from django.db import models
from accounts.models import CustomUser
# Create your models here.

class judgements(models.Model):
    filename = models.CharField(max_length=255,unique=True,null=False, default="file not exist.pdf")
    judgment_path = models.FileField(upload_to='judgment/')
    summary_path = models.FileField(upload_to='summary/')
    keywords = models.TextField()

    def __str__(self):
         return self.filename
    
class SearchFolders(models.Model):
    title = models.CharField(max_length=255)
    user_id = models.ForeignKey(CustomUser ,on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    last_modify = models.DateTimeField(auto_now=True)
    end_time = models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return self.title

class SearchJudgement(models.Model):
    searchfolders_id = models.ForeignKey(SearchFolders,on_delete=models.CASCADE)
    judgements_id = models.ForeignKey(judgements,  on_delete=models.CASCADE)

    # def __str__(self):
    #     return self.searchfolders_id