from django.db import models
from datetime import datetime
from django.db import models
from django.forms import model_to_dict
from shorter.settings import MEDIA_URL, STATIC_URL

# Create your models here.
class File(models.Model):
    name = models.CharField(max_length=150, verbose_name='Nombre', unique=True)
    file=  models.FileField(upload_to='urls/%Y/%m/%d', null=True, blank=True, verbose_name='URLS')
    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        item['file'] = self.get_file()
        return item

    def get_file(self):
        if self.file:
            return '{}{}'.format(MEDIA_URL, self.file)
        return '{}{}'.format(STATIC_URL, 'image/empty.png')

    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'
        ordering = ['id']


class Url(models.Model):
    long_url = models.URLField()
    short_id = models.SlugField()
    is_valida= models.BooleanField(default=False)
    redirect_count = models.IntegerField(default=0)
    pub_date = models.DateField(auto_now=True)
    fileid=models.ForeignKey(File, on_delete=models.CASCADE, verbose_name='File')
    def __str__(self):
        return "%s -- %s" % (self.long_url, self.short_id)

